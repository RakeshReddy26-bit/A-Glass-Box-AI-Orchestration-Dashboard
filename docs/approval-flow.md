# Approval Flow

## Purpose

The approval flow is the human-in-the-loop mechanism. It exists to ensure
that no irreversible, high-stakes, or uncertain action is taken without a
human seeing it first.

This is not a failsafe for a broken system. It is a deliberate design
choice for a working one.

---

## Trigger Conditions

An approval gate is raised when **any** of these conditions are met:

| Condition | Threshold | Example |
|-----------|-----------|---------|
| Risk score | ≥ 60 / 100 | Executor deploying to production |
| Agent confidence | < 60% | Coder uncertain about security change |
| Action type | Irreversible | Delete, send, deploy, publish |
| Scope | Customer-facing | Any change visible to end users |
| Financial impact | Any | Spend authorisation, pricing change |

Multiple conditions stack: a risky action by a low-confidence agent
raises a higher-priority gate.

---

## Step-by-Step Flow

### Step 1: Agent reaches decision point

An agent (typically Executor or Coder) is about to take an action.
Nicholas Core evaluates the action against the trigger conditions.

### Step 2: Gate raised

If a condition is met, Nicholas Core:
- Pauses the agent at the decision point
- Records the pending gate in system state
- Sets task status to `awaiting`

The dashboard reflects this immediately: the agent shows amber status,
the Work section shows the item in "Pending Approval."

### Step 3: Telegram notification

Nicholas Core sends a structured message to the designated Telegram
approval channel. The message contains:

- Gate ID and timestamp
- Which agent is waiting
- What action it wants to take
- Risk score and confidence score
- A plain-language description of the consequence
- Two response options: **APPROVE** or **REJECT**

### Step 4: Human decision

The human reads the Telegram message and responds with APPROVE or REJECT.
No login, no dashboard interaction, no context-switching required.
The decision is made in the same channel where work is already discussed.

### Step 5: Nicholas Core receives decision

- **APPROVE:** The agent resumes. The action is executed. Status returns
  to `running`. The dashboard reflects the change.
- **REJECT:** The agent is paused or redirected. The Planner is notified.
  A new sub-task is created to handle the rejection path.

### Step 6: State update

The dashboard reflects the resolved gate: the item disappears from the
"Pending Approval" section, and the activity feed logs the outcome.

---

## What Happens If No One Responds

Nicholas Core waits. The agent does not time out and act anyway.
Gates are blocking. The system is designed to sit and wait indefinitely
rather than take unauthorised action.

If a gate is not resolved within a configurable window, Nicholas Core
sends a follow-up reminder to Telegram.

---

## Visualisation in the Dashboard

The Work section shows all pending approval items with:

- Gate ID
- Title and description of the requested action
- Requesting agent
- Risk score (coloured: low / medium / high / critical)
- Agent confidence score
- The Telegram channel where approval must happen

A yellow banner at the top of the dashboard persists while any gate
is open, linking directly to the Work section.

The dashboard cannot approve or reject gates. This is intentional.
Approvals require a deliberate action in Telegram, not a button click
that could be misclicked.

---

## Design Principles

1. **Gates are infrequent by design.** Routine tasks never trigger them.
   If gates are firing constantly, the risk thresholds need recalibrating.

2. **Approval is one channel, not one interface.** Telegram is the
   approval surface — not the dashboard, not email, not a web app. This
   keeps the decision surface minimal and auditable.

3. **Rejection is not failure.** Rejecting a gate is valid feedback that
   teaches Nicholas Core what the human's risk tolerance looks like.
   Over time, fewer inappropriate gates should be raised.

4. **Audit trail is automatic.** Every gate, decision, and outcome is
   logged in Nicholas Core's state. The dashboard's Intel section
   surfaces this as the signal timeline.
