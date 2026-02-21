// ============================================================
// Glass-Box AI Orchestration Dashboard — Mock Data
// Scenario: Financial Research Pipeline (AAPL Analysis)
// ============================================================

// --- AGENTS ---
const AGENTS = [
  {
    id: 'atlas',
    name: 'Atlas',
    role: 'Orchestrator',
    description: 'Coordinates all agents, assigns tasks, manages pipeline flow',
    status: 'active',
    currentTask: 'Coordinating Q3 earnings research pipeline',
    tokenUsage: { used: 18420, allocated: 32000 },
    latencyMs: 245,
    costUsd: 1.84,
    trustScore: 96,
    confidenceScore: 92,
    riskLevel: 'low',
    lastAction: 'Dispatched SEC filing analysis task to Cipher',
    lastActionTime: '14:32:11',
    uptime: '4h 32m',
    tasksCompleted: 23,
    tasksFailed: 0,
    color: '#818cf8'
  },
  {
    id: 'scout',
    name: 'Scout',
    role: 'Research Agent',
    description: 'Gathers market data, news articles, SEC filings, and financial reports',
    status: 'active',
    currentTask: 'Retrieving AAPL 10-K filing from SEC EDGAR',
    tokenUsage: { used: 24100, allocated: 48000 },
    latencyMs: 1820,
    costUsd: 3.41,
    trustScore: 88,
    confidenceScore: 79,
    riskLevel: 'low',
    lastAction: 'Retrieved 14 market news articles from Reuters API',
    lastActionTime: '14:31:58',
    uptime: '4h 32m',
    tasksCompleted: 41,
    tasksFailed: 2,
    color: '#38bdf8'
  },
  {
    id: 'cipher',
    name: 'Cipher',
    role: 'Analysis Agent',
    description: 'Runs quantitative analysis, risk models, and financial calculations',
    status: 'active',
    currentTask: 'Running DCF valuation model on AAPL',
    tokenUsage: { used: 31200, allocated: 48000 },
    latencyMs: 3240,
    costUsd: 5.12,
    trustScore: 91,
    confidenceScore: 84,
    riskLevel: 'medium',
    lastAction: 'Completed sector correlation analysis \u2014 12 equities',
    lastActionTime: '14:30:44',
    uptime: '4h 32m',
    tasksCompleted: 18,
    tasksFailed: 1,
    color: '#4ade80'
  },
  {
    id: 'scribe',
    name: 'Scribe',
    role: 'Writer Agent',
    description: 'Drafts investment reports, summaries, and client-facing documents',
    status: 'idle',
    currentTask: null,
    tokenUsage: { used: 12800, allocated: 32000 },
    latencyMs: 890,
    costUsd: 2.07,
    trustScore: 93,
    confidenceScore: 87,
    riskLevel: 'low',
    lastAction: 'Completed draft of AAPL sector overview (2,400 words)',
    lastActionTime: '14:25:00',
    uptime: '4h 32m',
    tasksCompleted: 7,
    tasksFailed: 0,
    color: '#fbbf24'
  },
  {
    id: 'sentinel',
    name: 'Sentinel',
    role: 'Compliance Agent',
    description: 'Reviews outputs for regulatory compliance, flags violations, enforces standards',
    status: 'active',
    currentTask: 'Reviewing Scribe draft for SEC disclosure compliance',
    tokenUsage: { used: 8900, allocated: 24000 },
    latencyMs: 1100,
    costUsd: 1.22,
    trustScore: 97,
    confidenceScore: 94,
    riskLevel: 'low',
    lastAction: 'Flagged missing risk disclaimer in report section 3.2',
    lastActionTime: '14:31:20',
    uptime: '4h 32m',
    tasksCompleted: 15,
    tasksFailed: 0,
    color: '#f87171'
  }
];

// --- NICHOLAS (Human-in-the-Loop Director) ---
const NICHOLAS = {
  id: 'nicholas',
  name: 'Nicholas',
  role: 'AI Director \u2014 Human-in-the-Loop',
  status: 'online',
  pendingApprovals: 2,
  totalDecisions: 34,
  approvalRate: 88,
  avgResponseTime: '4m 12s',
  color: '#e879f9'
};

// --- SYSTEM METRICS ---
const SYSTEM_METRICS = {
  agentsOnline: 4,
  agentsIdle: 1,
  agentsError: 0,
  totalAgents: 5,
  totalTasksCompleted: 104,
  totalTasksPending: 8,
  pendingApprovals: 2,
  pipelinePhase: 'Research & Analysis',
  systemRisk: 'low',
  systemRiskScore: 18,
  totalTokensUsed: 95420,
  totalTokensAllocated: 184000,
  totalCostUsd: 13.66,
  avgLatencyMs: 1459,
  uptimeHours: 4.53
};

// --- ACTIVITY FEED ---
const ACTIVITY_FEED = [
  { id: 'evt-001', time: '14:32:11', agent: 'Atlas',    agentId: 'atlas',    text: 'Dispatched SEC filing analysis to Cipher \u2014 priority: high',            type: 'dispatch' },
  { id: 'evt-002', time: '14:31:58', agent: 'Scout',    agentId: 'scout',    text: 'Retrieved AAPL 10-K filing (147 pages) from SEC EDGAR',                type: 'data' },
  { id: 'evt-003', time: '14:31:45', agent: 'Sentinel', agentId: 'sentinel', text: 'Flagged missing risk disclaimer in Scribe draft section 3.2',          type: 'warning' },
  { id: 'evt-004', time: '14:31:20', agent: 'Cipher',   agentId: 'cipher',   text: 'Sector correlation analysis complete \u2014 R\u00b2: 0.847 across 12 equities', type: 'result' },
  { id: 'evt-005', time: '14:30:44', agent: 'Atlas',    agentId: 'atlas',    text: 'Pipeline checkpoint: Research phase 78% complete',                      type: 'status' },
  { id: 'evt-006', time: '14:30:10', agent: 'Scout',    agentId: 'scout',    text: 'Knowledge gap identified: Q3 earnings call transcript unavailable',     type: 'gap' },
  { id: 'evt-007', time: '14:29:33', agent: 'Cipher',   agentId: 'cipher',   text: 'DCF model initialized \u2014 discount rate: 8.5%, terminal growth: 2.5%',    type: 'result' },
  { id: 'evt-008', time: '14:28:50', agent: 'Sentinel', agentId: 'sentinel', text: 'Compliance scan passed for market data batch #12',                      type: 'success' },
  { id: 'evt-009', time: '14:28:15', agent: 'Scribe',   agentId: 'scribe',   text: 'Draft of AAPL sector overview submitted for compliance review',         type: 'status' },
  { id: 'evt-010', time: '14:27:30', agent: 'Atlas',    agentId: 'atlas',    text: 'Task dependency graph updated \u2014 3 new branches added',                  type: 'dispatch' },
  { id: 'evt-011', time: '14:26:55', agent: 'Scout',    agentId: 'scout',    text: 'Retrieved 14 market news articles from Reuters API',                    type: 'data' },
  { id: 'evt-012', time: '14:26:10', agent: 'Cipher',   agentId: 'cipher',   text: 'APPROVAL REQUIRED: Publish risk model with confidence below threshold', type: 'approval' },
  { id: 'evt-013', time: '14:25:40', agent: 'Atlas',    agentId: 'atlas',    text: 'Scribe assigned: draft client-facing summary for AAPL analysis',        type: 'dispatch' },
  { id: 'evt-014', time: '14:24:00', agent: 'Sentinel', agentId: 'sentinel', text: 'Regulatory update: SEC amendments to Reg S-K effective next quarter',   type: 'warning' },
  { id: 'evt-015', time: '14:23:20', agent: 'Scout',    agentId: 'scout',    text: 'Scraped 31 data points from Yahoo Finance \u2014 AAPL historical prices',    type: 'data' }
];

// --- SIMULATED EVENTS (for live feed) ---
const SIMULATED_EVENTS = [
  { agent: 'Scout',    agentId: 'scout',    text: 'Parsing SEC filing section: Management Discussion & Analysis',   type: 'data' },
  { agent: 'Cipher',   agentId: 'cipher',   text: 'Recalculating WACC with updated risk-free rate',                 type: 'result' },
  { agent: 'Atlas',    agentId: 'atlas',    text: 'Pipeline checkpoint: Analysis phase 42% complete',               type: 'status' },
  { agent: 'Sentinel', agentId: 'sentinel', text: 'Reviewing data sourcing attribution for batch #13',              type: 'status' },
  { agent: 'Scout',    agentId: 'scout',    text: 'Retrieved analyst consensus estimates \u2014 18 data points',         type: 'data' },
  { agent: 'Cipher',   agentId: 'cipher',   text: 'Sensitivity analysis: revenue growth \u00b12% impact on valuation',  type: 'result' },
  { agent: 'Atlas',    agentId: 'atlas',    text: 'Rebalanced task priority queue \u2014 2 tasks promoted',              type: 'dispatch' },
  { agent: 'Sentinel', agentId: 'sentinel', text: 'No new regulatory alerts in last scan cycle',                    type: 'success' },
  { agent: 'Scribe',   agentId: 'scribe',   text: 'Generating executive summary paragraph from Cipher analysis',    type: 'status' },
  { agent: 'Cipher',   agentId: 'cipher',   text: 'Monte Carlo simulation: processing batch 7,200 of 10,000',      type: 'result' },
  { agent: 'Scout',    agentId: 'scout',    text: 'Cross-referencing Bloomberg data with SEC disclosures',          type: 'data' },
  { agent: 'Atlas',    agentId: 'atlas',    text: 'Dependency resolved: Scribe unblocked for section 4 draft',      type: 'dispatch' }
];

// --- TOPOLOGY LINKS ---
const TOPOLOGY_LINKS = [
  { from: 'nicholas', to: 'atlas',    label: 'directs' },
  { from: 'atlas',    to: 'scout',    label: 'assigns research' },
  { from: 'atlas',    to: 'cipher',   label: 'assigns analysis' },
  { from: 'atlas',    to: 'scribe',   label: 'assigns writing' },
  { from: 'atlas',    to: 'sentinel', label: 'assigns review' },
  { from: 'scout',    to: 'cipher',   label: 'feeds data' },
  { from: 'scout',    to: 'scribe',   label: 'feeds data' },
  { from: 'cipher',   to: 'scribe',   label: 'feeds analysis' },
  { from: 'scribe',   to: 'sentinel', label: 'submits for review' },
  { from: 'sentinel', to: 'atlas',    label: 'reports compliance' },
  { from: 'sentinel', to: 'nicholas', label: 'escalates violations' }
];

// --- EXECUTION TRACE ---
const EXECUTION_TRACE = [
  {
    id: 'step-001', displayTime: '14:20:00', agent: 'Atlas', agentId: 'atlas',
    action: 'pipeline.initialize',
    toolCall: null,
    input: { goal: 'Produce comprehensive AAPL investment analysis report' },
    output: { taskCount: 14, estimatedDuration: '45 minutes', phases: ['Research', 'Analysis', 'Writing', 'Compliance'] },
    reasoning: 'CEO requested AAPL deep-dive. Decomposed into 4 sequential phases with parallel sub-tasks within each phase.',
    durationMs: 1200, status: 'completed'
  },
  {
    id: 'step-002', displayTime: '14:20:12', agent: 'Atlas', agentId: 'atlas',
    action: 'task.assign',
    toolCall: 'dispatchToAgent(scout, "research.sec_filing")',
    input: { ticker: 'AAPL', filingType: '10-K', source: 'SEC EDGAR' },
    output: { taskId: 'T-101', assignedTo: 'Scout', priority: 'high' },
    reasoning: 'SEC filing is the foundational data source. Must be retrieved before quantitative analysis. Highest priority.',
    durationMs: 340, status: 'completed'
  },
  {
    id: 'step-003', displayTime: '14:20:15', agent: 'Atlas', agentId: 'atlas',
    action: 'task.assign',
    toolCall: 'dispatchToAgent(scout, "research.market_news")',
    input: { ticker: 'AAPL', sources: ['Reuters', 'Bloomberg', 'WSJ'], lookbackDays: 30 },
    output: { taskId: 'T-102', assignedTo: 'Scout', priority: 'medium' },
    reasoning: 'Market news provides sentiment context. Runs in parallel with SEC filing retrieval. Lower priority as it supplements analysis.',
    durationMs: 280, status: 'completed'
  },
  {
    id: 'step-004', displayTime: '14:21:30', agent: 'Scout', agentId: 'scout',
    action: 'tool.call',
    toolCall: 'secEdgarAPI.fetch("AAPL", "10-K", "latest")',
    input: { endpoint: 'https://efts.sec.gov/LATEST/search-index?q=AAPL', format: 'json' },
    output: { pages: 147, fileSize: '2.4MB', filingDate: '2023-11-03' },
    reasoning: 'Using SEC EDGAR full-text search API for most recent 10-K. JSON format for structured extraction over HTML.',
    durationMs: 4200, status: 'completed'
  },
  {
    id: 'step-005', displayTime: '14:23:20', agent: 'Scout', agentId: 'scout',
    action: 'tool.call',
    toolCall: 'yahooFinance.historicalPrices("AAPL", "6mo", "1d")',
    input: { ticker: 'AAPL', period: '6mo', interval: '1d' },
    output: { dataPoints: 31, priceRange: { low: 167.44, high: 199.62 }, avgVolume: '58.3M' },
    reasoning: 'Historical price data needed for volatility input to DCF model. Six-month window covers recent earnings cycle.',
    durationMs: 2100, status: 'completed'
  },
  {
    id: 'step-006', displayTime: '14:25:00', agent: 'Scout', agentId: 'scout',
    action: 'tool.call',
    toolCall: 'reutersAPI.search("AAPL", { limit: 20, days: 30 })',
    input: { query: 'AAPL apple earnings revenue', limit: 20, daysBack: 30 },
    output: { articlesFound: 14, sentimentBreakdown: { positive: 8, neutral: 4, negative: 2 } },
    reasoning: 'Reuters returned 14 relevant articles. Sentiment skews positive, aligned with market consensus. Flagging AI spending theme.',
    durationMs: 3400, status: 'completed'
  },
  {
    id: 'step-007', displayTime: '14:26:10', agent: 'Cipher', agentId: 'cipher',
    action: 'analysis.initialize',
    toolCall: 'dcfModel.initialize({ discountRate: 0.085, terminalGrowth: 0.025 })',
    input: { filingData: '10-K parsed', historicalPrices: '31 data points', marketCap: '2.89T' },
    output: { modelReady: true, inputsValidated: true, missingInputs: ['Q3 earnings transcript'] },
    reasoning: 'Discount rate 8.5% reflects current risk-free rate plus equity risk premium. Terminal growth 2.5% conservative for large-cap tech. Q3 transcript flagged as gap.',
    durationMs: 1800, status: 'completed'
  },
  {
    id: 'step-008', displayTime: '14:28:15', agent: 'Scribe', agentId: 'scribe',
    action: 'document.draft',
    toolCall: 'generateReport("sector_overview", { ticker: "AAPL" })',
    input: { template: 'sector_overview', dataInputs: ['Reuters sentiment', 'SEC filing summary', 'price history'], targetLength: 2400 },
    output: { draftId: 'DOC-007', wordCount: 2412, sections: 5, readabilityScore: 72 },
    reasoning: 'Using sector overview template. Incorporating sentiment from Scout and filing highlights. Executive audience \u2014 readability 72 is appropriate.',
    durationMs: 12400, status: 'completed'
  },
  {
    id: 'step-009', displayTime: '14:30:10', agent: 'Scout', agentId: 'scout',
    action: 'research.gap_identified',
    toolCall: null,
    input: { query: 'AAPL Q3 2024 earnings call transcript' },
    output: { found: false, alternativeSources: ['Seeking Alpha (paywalled)', 'Company IR (not yet posted)'] },
    reasoning: 'Transcript unavailable in any accessible source. Creates a data gap for Cipher analysis. Reporting to Atlas for pipeline adjustment.',
    durationMs: 2800, status: 'completed'
  },
  {
    id: 'step-010', displayTime: '14:31:20', agent: 'Sentinel', agentId: 'sentinel',
    action: 'compliance.review',
    toolCall: 'complianceCheck(draftId: "DOC-007", ruleset: "SEC-Reg-SK")',
    input: { documentId: 'DOC-007', rules: ['risk_disclaimer', 'forward_looking_statements', 'data_sourcing'] },
    output: { passed: false, violations: [{ rule: 'risk_disclaimer', section: '3.2', severity: 'high' }], score: 82 },
    reasoning: 'Section 3.2 contains revenue projections without required risk disclaimer. High-severity SEC compliance issue. Flagging for Scribe revision.',
    durationMs: 3200, status: 'completed'
  },
  {
    id: 'step-011', displayTime: '14:31:45', agent: 'Cipher', agentId: 'cipher',
    action: 'analysis.risk_model',
    toolCall: 'riskModel.evaluate({ portfolio: "AAPL", confidence: 0.72 })',
    input: { model: 'monte_carlo', simulations: 10000, ticker: 'AAPL', timeHorizon: '12mo' },
    output: { valueAtRisk: '-12.4%', expectedReturn: '+8.7%', sharpeRatio: 0.94, confidenceInterval: '72%' },
    reasoning: 'Monte Carlo complete. Confidence 72% is below 80% threshold for autonomous publication. Requesting human approval before including in final report.',
    durationMs: 8400, status: 'pending_approval'
  },
  {
    id: 'step-012', displayTime: '14:32:11', agent: 'Atlas', agentId: 'atlas',
    action: 'task.assign',
    toolCall: 'dispatchToAgent(cipher, "analysis.sec_filing")',
    input: { document: 'AAPL 10-K (2023)', focus: ['revenue segments', 'risk factors', 'R&D spending'] },
    output: { taskId: 'T-108', assignedTo: 'Cipher', priority: 'high' },
    reasoning: 'SEC filing fully retrieved by Scout. Dispatching to Cipher for structured financial extraction. Prioritizing revenue segments for DCF model.',
    durationMs: 450, status: 'in_progress'
  }
];

// --- APPROVAL QUEUE (pending) ---
const APPROVAL_QUEUE = [
  {
    id: 'APR-001',
    displayTime: '14:26:12',
    agent: 'Cipher',
    agentId: 'cipher',
    title: 'Publish risk model with sub-threshold confidence',
    description: 'Cipher completed a Monte Carlo risk model for AAPL with 72% confidence. The publication threshold is 80%. Cipher requests permission to include this model in the final investment report with an explicit confidence disclaimer.',
    riskLevel: 'high',
    riskScore: 68,
    confidenceScore: 72,
    impact: 'If published with inaccurate projections, client investment decisions could be misinformed. Risk model covers 12-month forward projections.',
    requestedAction: 'Include Monte Carlo VaR analysis in final report Section 4 with confidence disclaimer',
    status: 'pending'
  },
  {
    id: 'APR-002',
    displayTime: '14:31:20',
    agent: 'Scribe',
    agentId: 'scribe',
    title: 'Distribute draft report to client stakeholders',
    description: 'Scribe has completed the AAPL sector overview draft (2,400 words). Sentinel flagged a missing risk disclaimer in section 3.2. Scribe requests approval to distribute after adding the disclaimer, without waiting for a full re-review.',
    riskLevel: 'medium',
    riskScore: 52,
    confidenceScore: 87,
    impact: 'Report distribution to 12 client stakeholders. Once sent, cannot be recalled. Contains forward-looking statements requiring proper disclaimers.',
    requestedAction: 'Add risk disclaimer to section 3.2 and distribute report via client portal',
    status: 'pending'
  }
];

// --- APPROVAL HISTORY ---
const APPROVAL_HISTORY = [
  { id: 'APR-H01', displayTime: '13:45:00', agent: 'Cipher',   agentId: 'cipher',   title: 'Use alternative data source for sector comparison',    decision: 'approved', decidedBy: 'Nicholas', responseTime: '2m 34s' },
  { id: 'APR-H02', displayTime: '12:30:00', agent: 'Scout',    agentId: 'scout',    title: 'Access premium Bloomberg terminal data',               decision: 'approved', decidedBy: 'Nicholas', responseTime: '5m 12s' },
  { id: 'APR-H03', displayTime: '11:15:00', agent: 'Scribe',   agentId: 'scribe',   title: 'Include speculative growth scenario in report',        decision: 'rejected', decidedBy: 'Nicholas', responseTime: '1m 48s' },
  { id: 'APR-H04', displayTime: '10:50:00', agent: 'Cipher',   agentId: 'cipher',   title: 'Run extended Monte Carlo simulation (50k iterations)',  decision: 'approved', decidedBy: 'Nicholas', responseTime: '3m 05s' },
  { id: 'APR-H05', displayTime: '10:10:00', agent: 'Sentinel', agentId: 'sentinel', title: 'Waive internal review for low-risk data summary',      decision: 'rejected', decidedBy: 'Nicholas', responseTime: '8m 22s' }
];

// --- DECISIONS ---
const DECISIONS = [
  {
    id: 'DEC-001',
    title: 'AAPL Sector Overview Report \u2014 Draft v1',
    outputSummary: 'A 2,400-word sector overview covering AAPL market position, competitive landscape, revenue trends, and risk factors.',
    producedBy: 'Scribe', producedById: 'scribe',
    confidenceScore: 87,
    displayTime: '14:28:15',
    contextChain: [
      { agent: 'Atlas',  agentId: 'atlas',  input: 'Goal: Produce AAPL investment analysis',           type: 'directive' },
      { agent: 'Scout',  agentId: 'scout',  input: '14 Reuters articles (sentiment: 57% positive)',    type: 'data' },
      { agent: 'Scout',  agentId: 'scout',  input: '10-K filing summary (147 pages parsed)',           type: 'data' },
      { agent: 'Scout',  agentId: 'scout',  input: 'Historical prices: 31 data points, 6mo window',   type: 'data' },
      { agent: 'Cipher', agentId: 'cipher', input: 'Sector correlation: R\u00b2 0.847 across 12 equities', type: 'analysis' }
    ]
  },
  {
    id: 'DEC-002',
    title: 'DCF Valuation Model \u2014 AAPL',
    outputSummary: 'Discounted cash flow model projecting intrinsic value with 8.5% discount rate and 2.5% terminal growth rate.',
    producedBy: 'Cipher', producedById: 'cipher',
    confidenceScore: 84,
    displayTime: '14:29:33',
    contextChain: [
      { agent: 'Atlas',  agentId: 'atlas',  input: 'Goal: Run quantitative analysis on AAPL',          type: 'directive' },
      { agent: 'Scout',  agentId: 'scout',  input: '10-K financials (revenue, COGS, OpEx, CapEx)',     type: 'data' },
      { agent: 'Scout',  agentId: 'scout',  input: 'Historical price data (6mo daily)',                type: 'data' },
      { agent: 'Cipher', agentId: 'cipher', input: 'Risk-free rate: 4.2% (10Y Treasury)',              type: 'assumption' },
      { agent: 'Cipher', agentId: 'cipher', input: 'Equity risk premium: 4.3% (Damodaran)',            type: 'assumption' }
    ]
  },
  {
    id: 'DEC-003',
    title: 'Monte Carlo Risk Assessment \u2014 AAPL',
    outputSummary: '10,000-simulation Monte Carlo yielding VaR of -12.4% and expected return of +8.7% over 12-month horizon.',
    producedBy: 'Cipher', producedById: 'cipher',
    confidenceScore: 72,
    displayTime: '14:31:45',
    contextChain: [
      { agent: 'Atlas',    agentId: 'atlas',    input: 'Goal: Assess investment risk for AAPL position',    type: 'directive' },
      { agent: 'Cipher',   agentId: 'cipher',   input: 'DCF model outputs (intrinsic value estimate)',      type: 'analysis' },
      { agent: 'Scout',    agentId: 'scout',    input: 'Historical volatility data',                        type: 'data' },
      { agent: 'Scout',    agentId: 'scout',    input: 'Macro indicators (Fed rate, CPI, unemployment)',    type: 'data' },
      { agent: 'Sentinel', agentId: 'sentinel', input: 'Confidence below 80% threshold \u2014 gate required',    type: 'compliance' }
    ]
  },
  {
    id: 'DEC-004',
    title: 'Compliance Flag \u2014 Missing Risk Disclaimer',
    outputSummary: 'Sentinel identified missing risk disclaimer in Scribe draft section 3.2. Forward-looking projections require SEC Reg S-K disclaimers.',
    producedBy: 'Sentinel', producedById: 'sentinel',
    confidenceScore: 94,
    displayTime: '14:31:20',
    contextChain: [
      { agent: 'Atlas',    agentId: 'atlas',    input: 'Goal: Review all outputs for regulatory compliance', type: 'directive' },
      { agent: 'Scribe',   agentId: 'scribe',   input: 'Draft DOC-007: AAPL Sector Overview (2,400 words)', type: 'document' },
      { agent: 'Sentinel', agentId: 'sentinel', input: 'Ruleset: SEC Reg S-K forward-looking statements',   type: 'compliance' },
      { agent: 'Sentinel', agentId: 'sentinel', input: 'Finding: 3 sentences without disclaimer in \u00a73.2',   type: 'finding' }
    ]
  }
];

// --- AUDIT LOG ---
const AUDIT_LOG = [
  { id: 'AUD-001', displayTime: '14:32:11', agent: 'Atlas',    agentId: 'atlas',    actionType: 'task.assign',       description: 'Assigned SEC filing analysis to Cipher',                     riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-002', displayTime: '14:31:58', agent: 'Scout',    agentId: 'scout',    actionType: 'data.retrieve',     description: 'Retrieved AAPL 10-K from SEC EDGAR (147 pages)',             riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-003', displayTime: '14:31:45', agent: 'Cipher',   agentId: 'cipher',   actionType: 'analysis.complete', description: 'Monte Carlo risk model completed \u2014 confidence 72%',          riskLevel: 'medium', outcome: 'pending_approval' },
  { id: 'AUD-004', displayTime: '14:31:20', agent: 'Sentinel', agentId: 'sentinel', actionType: 'compliance.flag',   description: 'Flagged missing risk disclaimer in DOC-007 section 3.2',      riskLevel: 'high',   outcome: 'violation_flagged' },
  { id: 'AUD-005', displayTime: '14:30:44', agent: 'Cipher',   agentId: 'cipher',   actionType: 'analysis.complete', description: 'Sector correlation analysis complete \u2014 12 equities',          riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-006', displayTime: '14:30:10', agent: 'Scout',    agentId: 'scout',    actionType: 'research.gap',      description: 'Knowledge gap: Q3 earnings transcript unavailable',          riskLevel: 'medium', outcome: 'gap_reported' },
  { id: 'AUD-007', displayTime: '14:29:33', agent: 'Cipher',   agentId: 'cipher',   actionType: 'analysis.init',     description: 'DCF model initialized \u2014 8.5% discount rate',                  riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-008', displayTime: '14:28:50', agent: 'Sentinel', agentId: 'sentinel', actionType: 'compliance.scan',   description: 'Compliance scan passed for market data batch #12',            riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-009', displayTime: '14:28:15', agent: 'Scribe',   agentId: 'scribe',   actionType: 'document.draft',    description: 'AAPL sector overview draft completed (2,400 words)',          riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-010', displayTime: '14:27:30', agent: 'Atlas',    agentId: 'atlas',    actionType: 'task.update',       description: 'Task dependency graph updated \u2014 3 new branches',              riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-011', displayTime: '14:26:55', agent: 'Scout',    agentId: 'scout',    actionType: 'data.retrieve',     description: 'Retrieved 14 articles from Reuters API',                     riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-012', displayTime: '14:26:12', agent: 'Cipher',   agentId: 'cipher',   actionType: 'approval.request',  description: 'Approval requested: publish sub-threshold risk model',       riskLevel: 'high',   outcome: 'awaiting_human' },
  { id: 'AUD-013', displayTime: '14:25:40', agent: 'Atlas',    agentId: 'atlas',    actionType: 'task.assign',       description: 'Assigned client summary draft task to Scribe',               riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-014', displayTime: '14:25:00', agent: 'Scribe',   agentId: 'scribe',   actionType: 'document.draft',    description: 'Completed AAPL sector overview \u2014 submitted for review',       riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-015', displayTime: '14:24:00', agent: 'Sentinel', agentId: 'sentinel', actionType: 'compliance.update', description: 'Regulatory update: SEC Reg S-K amendments noted',             riskLevel: 'medium', outcome: 'logged' },
  { id: 'AUD-016', displayTime: '14:23:20', agent: 'Scout',    agentId: 'scout',    actionType: 'data.retrieve',     description: 'Scraped 31 AAPL historical price data points',               riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-017', displayTime: '14:20:12', agent: 'Atlas',    agentId: 'atlas',    actionType: 'task.assign',       description: 'Assigned SEC filing retrieval to Scout \u2014 priority high',      riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-018', displayTime: '14:20:00', agent: 'Atlas',    agentId: 'atlas',    actionType: 'pipeline.init',     description: 'Pipeline initialized: AAPL investment analysis \u2014 14 tasks',   riskLevel: 'low',    outcome: 'success' },
  { id: 'AUD-019', displayTime: '13:45:00', agent: 'Nicholas', agentId: 'nicholas', actionType: 'approval.decision', description: 'APPROVED: Use alternative data source for sector comparison', riskLevel: 'medium', outcome: 'approved' },
  { id: 'AUD-020', displayTime: '12:30:00', agent: 'Nicholas', agentId: 'nicholas', actionType: 'approval.decision', description: 'APPROVED: Access premium Bloomberg terminal data',            riskLevel: 'medium', outcome: 'approved' }
];

// --- MEMORY STATE ---
const MEMORY_STATE = [
  {
    agentId: 'atlas', agentName: 'Atlas', color: '#818cf8',
    memorySlots: 8,
    tokenUsage: { used: 18420, allocated: 32000 },
    contextItems: [
      { type: 'directive', label: 'Current pipeline goal',                 tokens: 340 },
      { type: 'state',     label: 'Task dependency graph (14 nodes)',      tokens: 2100 },
      { type: 'state',     label: 'Agent status registry',                tokens: 480 },
      { type: 'history',   label: 'Last 20 dispatch decisions',           tokens: 3200 },
      { type: 'config',    label: 'Agent capability matrix',              tokens: 890 },
      { type: 'config',    label: 'Risk threshold configuration',         tokens: 420 },
      { type: 'state',     label: 'Pipeline checkpoint: phase 2 of 4',    tokens: 150 },
      { type: 'history',   label: 'Approval decision history (5 records)',tokens: 1240 }
    ],
    dataSources: ['Pipeline configuration', 'Agent capability registry', 'Task queue', 'Approval history']
  },
  {
    agentId: 'scout', agentName: 'Scout', color: '#38bdf8',
    memorySlots: 6,
    tokenUsage: { used: 24100, allocated: 48000 },
    contextItems: [
      { type: 'data',      label: 'AAPL 10-K filing (parsed, 147 pages)',     tokens: 12400 },
      { type: 'data',      label: 'Reuters articles (14, summarized)',        tokens: 4200 },
      { type: 'data',      label: 'Yahoo Finance prices (31 points)',        tokens: 890 },
      { type: 'directive', label: 'Active research queries (3)',              tokens: 420 },
      { type: 'state',     label: 'Known knowledge gaps (2 items)',          tokens: 180 },
      { type: 'config',    label: 'API credentials and rate limits',         tokens: 340 }
    ],
    dataSources: ['SEC EDGAR API', 'Reuters API', 'Yahoo Finance API', 'Bloomberg (pending)', 'Internal KB']
  },
  {
    agentId: 'cipher', agentName: 'Cipher', color: '#4ade80',
    memorySlots: 7,
    tokenUsage: { used: 31200, allocated: 48000 },
    contextItems: [
      { type: 'data',     label: 'AAPL financial statements (3 years)',         tokens: 8800 },
      { type: 'data',     label: 'Historical price series (6 months)',          tokens: 1200 },
      { type: 'analysis', label: 'DCF model parameters + intermediate results', tokens: 6400 },
      { type: 'analysis', label: 'Monte Carlo output (10k runs)',              tokens: 4200 },
      { type: 'analysis', label: 'Sector correlation matrix (12 equities)',    tokens: 3100 },
      { type: 'config',   label: 'Model assumptions and thresholds',           tokens: 560 },
      { type: 'state',    label: 'Pending: SEC filing deep analysis',          tokens: 280 }
    ],
    dataSources: ['Scout data feed', 'Financial model library', 'Macro indicators DB', 'Risk model templates']
  },
  {
    agentId: 'scribe', agentName: 'Scribe', color: '#fbbf24',
    memorySlots: 5,
    tokenUsage: { used: 12800, allocated: 32000 },
    contextItems: [
      { type: 'document',  label: 'Current draft: AAPL Sector Overview v1',   tokens: 4800 },
      { type: 'data',      label: 'Scout research summaries (3 batches)',     tokens: 3200 },
      { type: 'analysis',  label: 'Cipher analysis highlights',              tokens: 2100 },
      { type: 'config',    label: 'Report templates and style guide',        tokens: 1400 },
      { type: 'directive', label: 'Writing assignments from Atlas',          tokens: 380 }
    ],
    dataSources: ['Scout summaries', 'Cipher analysis outputs', 'Report template library', 'Style guide']
  },
  {
    agentId: 'sentinel', agentName: 'Sentinel', color: '#f87171',
    memorySlots: 5,
    tokenUsage: { used: 8900, allocated: 24000 },
    contextItems: [
      { type: 'config',  label: 'SEC Reg S-K compliance ruleset',         tokens: 3400 },
      { type: 'config',  label: 'Internal compliance policies',           tokens: 1800 },
      { type: 'state',   label: 'Current review queue (2 documents)',     tokens: 420 },
      { type: 'history', label: 'Past compliance findings (8 records)',   tokens: 1600 },
      { type: 'data',    label: 'Regulatory update log (Q4 2023\u2013Q1 2024)', tokens: 980 }
    ],
    dataSources: ['SEC regulatory database', 'Internal compliance rulebook', 'Scribe draft documents', 'Regulatory update feed']
  }
];
