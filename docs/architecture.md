# Architecture

## Overview

The Glass Box AI Orchestration system has three distinct layers that never
overlap:

```
┌─────────────────────────────────────────────────────┐
│  OBSERVATION LAYER                                  │
│  dashboard/index.html  ←  this file                 │
│  Read-only. No writes. No commands.                 │
└────────────────────────┬────────────────────────────┘
                         │ reads state (static data / future: API)
┌────────────────────────▼────────────────────────────┐
│  APPROVAL LAYER                                     │
│  Telegram  ←  human-in-the-loop channel             │
│  Approval requests arrive. Decisions are sent back. │
└────────────────────────┬────────────────────────────┘
                         │ gates execution
┌────────────────────────▼────────────────────────────┐
│  EXECUTION LAYER                                    │
│  Nicholas Core  ←  agent runtime                   │
│  Plans, delegates, executes, stores memory.         │
└─────────────────────────────────────────────────────┘
```

These layers communicate in one direction: bottom-up for state, top-down
for approval decisions. The dashboard is never in this loop — it is
a passive observer attached to the side.

---

## Component Breakdown

### dashboard/index.html

- Pure HTML + Tailwind CSS (CDN) + vanilla JavaScript
- Zero runtime dependencies
- All data is inline (static fixtures representing live state)
- Renders five logical views: Now, Agents, Work, Intel, You
- Uses no fetch calls, no WebSockets, no external APIs
- Designed to be upgraded: replace static data arrays with a fetch from a
  local JSON export or a read-only REST endpoint without changing the UI

### Nicholas Core (agent runtime)

- Orchestrates all agent activity
- Assigns tasks, routes outputs, manages inter-agent communication
- Writes structured state snapshots that the dashboard would consume
- Raises approval gates when risk thresholds are crossed
- Never modified by this dashboard

### Telegram (approval channel)

- Receives gate notifications from Nicholas Core
- Human reviews the request and responds approve / reject
- Nicholas Core listens for this response and resumes or aborts
- The dashboard displays which items are currently pending in this channel

---

## Data Flow

```
Agent completes step
        ↓
Nicholas Core evaluates risk score
        ↓
Score < threshold  →  continue automatically
Score ≥ threshold  →  raise approval gate
                             ↓
                      Telegram notification sent
                             ↓
                      Dashboard shows "Pending Approval"
                             ↓
                      Human approves / rejects in Telegram
                             ↓
                      Nicholas Core resumes / aborts
                             ↓
                      Dashboard state updates
```

---

## Upgrade Path (Static → Live)

The current dashboard uses inline JS data arrays. To connect it to a live
system, replace the data constants in `<script>` with a `fetch()` call to a
read-only JSON endpoint served by Nicholas Core:

```js
// Current (static)
const AGENTS = [ { id: 'planner', ... }, ... ];

// Future (live, read-only)
const AGENTS = await fetch('/api/state/agents').then(r => r.json());
```

No other changes to the HTML or CSS are needed.

---

## Security Posture

- The dashboard has no authentication (it is a local file)
- It has no write surface — there are no forms, no POST calls
- It cannot issue commands, modify agent state, or trigger tasks
- The only external network call is loading Tailwind CSS from CDN on first
  open (can be replaced with a local copy for fully offline use)
