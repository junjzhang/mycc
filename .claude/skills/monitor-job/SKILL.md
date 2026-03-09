---
name: monitor-job
description: >-
  Launch a background agent to monitor a long-running remote job (K8s, SLURM, CI).
  Use when submitting jobs that need async monitoring.
  Keywords: monitor, watch job, background agent, submit and watch, check job status.
---

# Monitor Job

Launch a background agent to watch a remote job and report back on completion or failure. Keeps the main conversation unblocked.

## When to Use

- After submitting any long-running job (training, inference, CI, deploy)
- When the user says "monitor this", "watch this job", "check on the job"
- Proactively after submitting a job that will take >5 minutes

## How to Launch

```python
Agent(
    description="Monitor <short-description>",
    prompt=<context-specific prompt>,
    run_in_background=True,
)
```

## Writing the Prompt

The prompt should tell the agent **what to check**, **how to check**, and **when to stop**. Include:

1. **Job identifier** — how to find the job (pod name, job ID, URL, etc.)
2. **What to observe** — specific log files, commands, or endpoints to check
3. **Success criteria** — what "working" looks like (read from the project/example CLAUDE.md if available)
4. **Failure patterns** — what errors to watch for
5. **Check interval** — how often to poll (typically 3-5 min)
6. **Timeout** — max monitoring duration

## Key Points

- Always use `run_in_background=True` — never block the main conversation
- Agent auto-notifies on completion — no need to poll
- Can check intermediate status via `Read` on the agent's output file
- Read any project-specific CLAUDE.md for log paths and success criteria before writing the prompt
- Tell the agent to report: timeline, outcome, errors found
