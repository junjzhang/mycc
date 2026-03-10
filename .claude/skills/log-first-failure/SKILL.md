---
name: log-first-failure
description: >-
  Build a first-failure timeline for distributed incidents. Use when debugging
  crashes, hangs, watchdog timeouts, collective mismatches, or cascading errors
  where the last error is often not the root cause.
---

# Log First Failure

## Purpose

Find the first meaningful failure quickly and avoid being misled by downstream crash noise.

## When to Use

Use this playbook when:
- Multiple components fail close in time
- Logs show watchdog, timeout, EOF, actor-died, connection reset, or retries
- It is unclear whether infra, runtime, model, or communication failed first

## Core Principle

The first loud error is often not the first causal error.

Always identify:
1. First local failure event
2. First cross-component consequence
3. Final crash envelope

## Workflow

### 1) Build a single merged timeline

Track both:
- **Control plane**: pause/resume/sync/update/signal/dispatch
- **Data plane**: collective/kernel/transfer/execution/request handling

Create a compact timeline table:

```text
time | component | event | class(control/data) | note
```

### 2) Mark the first meaningful error

Prefer earliest local failure that indicates unhealthy state in one component.

Do not select these as root cause by default:
- Watchdog timeout
- Connection closed by peer
- Actor died unexpectedly
- End of file / broken pipe

These are often cascades.

### 3) Split root-cause candidates vs cascades

- **Candidate**: earliest event that can explain all later failures
- **Cascade**: events that require a prior failure to exist

### 4) Validate ordering assumptions

Check whether timestamp ordering across files is reliable. If clocks differ, use protocol sequence numbers or deterministic markers when available.

### 5) Produce a minimal incident summary

Required fields:
- `first_failure_component`
- `first_failure_timestamp`
- `triggering_event`
- `cascading_errors`
- `top_hypotheses`
- `confidence`

## Output Contract

Return:
1. One-paragraph diagnosis
2. Ordered evidence list (earliest -> latest)
3. Ranked root-cause hypotheses with confidence

## Common Failure Modes

- Picking the last timeout as root cause
- Mixing control-plane and data-plane events
- Ignoring late-message races around pause/resume
- Treating retries/restarts as primary failures
