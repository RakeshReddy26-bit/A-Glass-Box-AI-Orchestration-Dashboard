/**
 * Glass Box AI Dashboard — Backend Connection Layer
 * Bridges the dashboard frontend to the Python backend.
 * Falls back silently to mock data when backend is offline.
 */
(function () {
  'use strict';

  // Auto-detect API base: if served by backend, use same origin; else localhost
  var loc = window.location;
  var API_BASE = (loc.protocol === 'file:') ? 'http://localhost:8000' : loc.origin;
  var wsProto = (loc.protocol === 'https:') ? 'wss:' : 'ws:';
  var WS_URL = (loc.protocol === 'file:') ? 'ws://localhost:8000/ws' : wsProto + '//' + loc.host + '/ws';

  window.BACKEND_LIVE = false;
  var ws = null;
  var reconnectTimer = null;

  // ── Check Backend Health ──────────────────────────────────

  function checkBackend() {
    fetch(API_BASE + '/api/health', { method: 'GET', mode: 'cors' })
      .then(function (resp) { return resp.json(); })
      .then(function (data) {
        if (data.status === 'ok') {
          window.BACKEND_LIVE = true;
          updateFooter(true, data.claude_api);
          connectWebSocket();
          overrideSendDirective();
          overrideHandleDecision();
          console.log('[Glass Box] Backend connected. Claude API:', data.claude_api);
        }
      })
      .catch(function () {
        window.BACKEND_LIVE = false;
        updateFooter(false);
        // Retry every 10 seconds
        setTimeout(checkBackend, 10000);
      });
  }

  // ── WebSocket Connection ──────────────────────────────────

  function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) return;

    try {
      ws = new WebSocket(WS_URL);

      ws.onopen = function () {
        console.log('[Glass Box] WebSocket connected');
        if (reconnectTimer) {
          clearTimeout(reconnectTimer);
          reconnectTimer = null;
        }
      };

      ws.onmessage = function (event) {
        try {
          var data = JSON.parse(event.data);
          handleWSMessage(data);
        } catch (e) {
          console.warn('[Glass Box] WS parse error:', e);
        }
      };

      ws.onclose = function () {
        console.log('[Glass Box] WebSocket disconnected');
        ws = null;
        // Reconnect after 5 seconds
        reconnectTimer = setTimeout(connectWebSocket, 5000);
      };

      ws.onerror = function () {
        ws = null;
      };

      // Send ping every 30 seconds to keep connection alive
      setInterval(function () {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 30000);

    } catch (e) {
      console.warn('[Glass Box] WebSocket error:', e);
    }
  }

  function handleWSMessage(data) {
    if (data.type === 'activity' && data.event) {
      // Push new event to the activity feed
      if (typeof ACTIVITY_FEED !== 'undefined') {
        ACTIVITY_FEED.unshift(data.event);
        if (ACTIVITY_FEED.length > 15) ACTIVITY_FEED.pop();
        if (typeof window.renderFeed === 'function') {
          window.renderFeed(ACTIVITY_FEED);
        }
      }
    }

    if (data.type === 'decision' && data.decision) {
      // A decision was made (could be from Telegram or another client)
      if (typeof window.showToast === 'function') {
        var toastType = data.decision.decision === 'approved' ? 'success' :
                        data.decision.decision === 'paused' ? 'warning' : 'error';
        window.showToast(data.decision.id + ' ' + data.decision.decision, toastType);
      }
    }

    if (data.type === 'connected') {
      console.log('[Glass Box] Received server state:', data.agents ? Object.keys(data.agents).length + ' agents' : 'no agents');
    }
  }

  // ── Override sendDirective() ──────────────────────────────

  function overrideSendDirective() {
    // Save the original sendDirective
    var originalSend = window.sendDirective;

    window.sendDirective = function () {
      if (!window.BACKEND_LIVE) {
        // Fall back to original mock behavior
        if (typeof originalSend === 'function') originalSend();
        return;
      }

      var input = document.getElementById('console-input');
      var select = document.getElementById('console-target');
      if (!input || !select) return;

      var text = input.value.trim();
      if (!text) return;

      var targetId = select.value;
      var targetName = window.agentNames ? window.agentNames[targetId] || targetId : targetId;
      var ts = typeof window.getTimestamp === 'function' ? window.getTimestamp() : new Date().toTimeString().slice(0, 8);

      // Add outgoing message to chat
      if (typeof window.chatMessages !== 'undefined') {
        window.chatMessages.push({
          direction: 'out',
          time: ts,
          target: targetName,
          text: text,
        });
        if (typeof window.renderChat === 'function') window.renderChat();
      }

      // Show typing indicator
      var respondingAgents = targetId === 'all'
        ? ['atlas', 'scout', 'cipher', 'scribe', 'sentinel']
        : [targetId];
      if (typeof window.showTyping === 'function') {
        window.showTyping(respondingAgents.length === 1 ? targetName : 'Agents');
      }

      if (typeof window.showToast === 'function') {
        window.showToast('Sent to ' + targetName, 'success');
      }

      input.value = '';

      // POST to backend
      fetch(API_BASE + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors',
        body: JSON.stringify({ agent: targetId, message: text }),
      })
        .then(function (resp) { return resp.json(); })
        .then(function (data) {
          if (typeof window.hideTyping === 'function') window.hideTyping();

          if (data.responses) {
            // Multiple agent responses (all agents)
            data.responses.forEach(function (r) {
              if (typeof window.chatMessages !== 'undefined') {
                window.chatMessages.push({
                  direction: 'in',
                  time: r.time || ts,
                  agent: r.agent,
                  agentId: r.agentId,
                  text: r.response,
                });
              }
            });
          } else if (data.response) {
            // Single agent response
            if (typeof window.chatMessages !== 'undefined') {
              window.chatMessages.push({
                direction: 'in',
                time: data.time || ts,
                agent: data.agent,
                agentId: data.agentId,
                text: data.response,
              });
            }
          }

          if (typeof window.renderChat === 'function') window.renderChat();
        })
        .catch(function (err) {
          console.error('[Glass Box] Chat error:', err);
          if (typeof window.hideTyping === 'function') window.hideTyping();

          // Fallback to mock behavior
          if (typeof originalSend === 'function') {
            // Re-set the input value and call original
            input.value = text;
            window.sendDirective = originalSend;
            originalSend();
            window.sendDirective = arguments.callee;
          }

          if (typeof window.showToast === 'function') {
            window.showToast('Backend error — using mock responses', 'warning');
          }
        });
    };
  }

  // ── Override handleDecision() ──────────────────────────────

  function overrideHandleDecision() {
    var originalHandle = window.handleDecision;

    window.handleDecision = function (id, decision) {
      if (!window.BACKEND_LIVE) {
        if (typeof originalHandle === 'function') originalHandle(id, decision);
        return;
      }

      // POST decision to backend
      fetch(API_BASE + '/api/approvals/' + id + '/decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors',
        body: JSON.stringify({ decision: decision }),
      })
        .then(function (resp) { return resp.json(); })
        .then(function (data) {
          if (data.success) {
            // Still use original handler for UI updates
            if (typeof originalHandle === 'function') originalHandle(id, decision);
          } else {
            if (typeof window.showToast === 'function') {
              window.showToast('Decision error: ' + (data.error || 'unknown'), 'error');
            }
          }
        })
        .catch(function () {
          // Fallback to local behavior
          if (typeof originalHandle === 'function') originalHandle(id, decision);
        });
    };
  }

  // ── Update Footer ──────────────────────────────────────────

  function updateFooter(connected, claudeApi) {
    var footerSpans = document.querySelectorAll('footer span');
    if (footerSpans.length >= 2) {
      if (connected) {
        var apiStatus = claudeApi ? 'Claude API active' : 'No API key';
        footerSpans[1].innerHTML =
          '<span style="color:var(--green);">&#9679;</span> Connected to backend &middot; ' + apiStatus;
      } else {
        footerSpans[1].textContent = 'Static \u00b7 No server \u00b7 Open index.html';
      }
    }
  }

  // ── Init ───────────────────────────────────────────────────

  // Wait for DOM and other scripts to load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      setTimeout(checkBackend, 500);
    });
  } else {
    setTimeout(checkBackend, 500);
  }

})();
