# Mental Model

## The Core Distinction

There are two ways to deploy an AI agent:

**Black box:**
```
You → [goal] → Agent → [output] → You
                 ↑
           (invisible)
```

**Glass box:**
```
You → [goal] → Agent → [output] → You
                 ↑
         (this dashboard)
         status / confidence / risk / gates
```

The agent runtime is the same. The difference is observability.
This dashboard is the glass.

---

## What "Read-Only" Actually Means

Read-only does not mean "passive and useless." It means:

- You can see everything that matters without being able to accidentally
  break anything
- The surface area for mistakes is zero — there is nothing to click
  that causes a side effect
- The dashboard is safe to open, share screenshares of, and leave running
  on a second monitor without any risk

When you need to act, you act in Telegram. When you need to observe,
you open this dashboard. The two surfaces are intentionally separate.

---

## Confidence vs Risk

These two numbers mean different things and should not be confused:

| Metric | What it measures | Who sets it |
|--------|-----------------|-------------|
| **Confidence** | How certain the agent is that its output is correct | The agent itself (self-assessed) |
| **Risk** | How consequential the action is if the agent is wrong | Nicholas Core (based on action type + reversibility) |

An agent can be **high confidence, high risk** — it is sure of its plan
but the plan involves irreversible production changes.

An agent can be **low confidence, low risk** — it is uncertain about a
classification task, but being wrong costs nothing.

Both dimensions are shown independently in the Agents and Work sections.

---

## Approval Gates Are Not Bottlenecks

A common reaction to human-in-the-loop systems: "this will slow everything
down."

The gates are scoped to high-risk actions only. Low-risk work continues
uninterrupted. The system is designed so that 90%+ of tasks never require
a gate.

Gates exist for actions that are:
- Irreversible (deployments, sends, deletes)
- High-stakes (financial, customer-facing, security-sensitive)
- Uncertain (agent confidence below threshold)

Everything else runs automatically.

---

## The Role of Nicholas Core

Nicholas Core is not a single agent. It is the orchestration runtime:
the layer that decides which agent works on which task, routes outputs
between agents, stores shared memory, and enforces approval gates.

Think of it as the operating system for the agent team. Agents are
processes. Nicholas Core is the kernel.

This dashboard is a monitoring terminal attached to that kernel.
It reads kernel state. It does not execute kernel commands.

---

## Why Not Build This in React / Next.js?

Frameworks add: build steps, dependency trees, node_modules, environment
variables, deployment infrastructure, and cognitive overhead for anyone
reading the code later.

For a read-only dashboard where the primary value is **transparency and
inspectability**, these costs are pure waste.

The design constraint — pure HTML, Tailwind CDN, vanilla JS — means:

1. Anyone can audit the full UI in one file in under 10 minutes
2. There is nothing to install, update, or break
3. The dashboard works offline, across machines, without a dev server
4. It can be shared as a single file attachment
