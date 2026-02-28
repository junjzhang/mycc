---
name: observe-act-loop
description: >-
  Execute-observe-diagnose-fix loop for verifying code changes through execution.
  Covers local tests (pytest, unittest), local services, remote jobs (kubectl, submit),
  CI/CD pipelines, and cluster deployments. Use when code correctness requires
  runtime verification. Keywords: run tests, submit, deploy, verify, debug, resubmit,
  pytest, kubectl, check logs, watch, diagnose, tail logs.
---

# Observe-Act Loop

Unified methodology for the execute-observe-diagnose-fix cycle. All runtime verification follows this pattern regardless of scale.

## When to Enter the Loop

**Core question: does the change require execution to verify correctness?**

Enter the loop when:
- Changed logic code with test coverage available
- Changed runtime behavior (process management, distributed config, server code)
- User reported an execution error, fix needs verification
- User explicitly requests: run, test, submit, verify, deploy, debug

Do NOT enter the loop when:
- Only docs, comments, type hints, or formatting changed
- Pure dead code deletion
- Change is obviously correct and user didn't ask to verify (e.g. fixing a typo)

**Key: not every code change needs a loop.** Entering the loop has cost (especially remote jobs). Ask yourself: **how confident am I that this change is correct without executing it?** If not confident enough, enter the loop.

## Before Starting

Read the project's CLAUDE.md and any case-specific CLAUDE.md to find:
1. **Execute** commands (test, submit, start)
2. **Observe** methods (log paths, pod discovery, health checks)
3. **Success criteria** (expected output, log lines, test pass counts)

If any of these are missing, ask the user before proceeding.

## The Loop

```
Execute → Observe → Diagnose → Fix → Re-execute
   ↑                                      |
   └──────────────────────────────────────┘
```

### Step 1: Execute

Run the appropriate command for the verification level:

| Level | Example commands |
|---|---|
| Local test | `pytest`, `pixi run -e dev pytest` |
| Local service | Start server, curl endpoint |
| Remote job | `pixi run submit examples/<name>/launch.sh` |
| CI/CD | `git push`, trigger pipeline |

### Step 2: Observe

Collect execution output. Where to look depends on the level:

| Level | Observation method |
|---|---|
| Local test | Read test output directly |
| Local service | Check stdout/stderr, probe endpoints |
| Remote job | `kubectl get pods \| grep <id>`, `kubectl exec <pod> -- tail -f <log>` |
| CI/CD | `gh run view`, check pipeline UI |

**For remote jobs:** Follow the project's log location pattern. Typical: `logs/<experiment_id>/node_<n>/<process>.log`

### Step 3: Diagnose

Follow these principles:
1. **Follow the signal chain.** Check components in order, from entry point to failure.
2. **Find the boundary.** What was the last successful step? What was the first failure?
3. **Don't skip ahead.** No guessing. Read the actual error, trace the actual call path.
4. **Check the obvious first.** Typos, wrong paths, missing env vars, import errors — before diving into logic bugs.

Common failure categories:
- **Import/syntax error** — immediate, fix and re-execute
- **Configuration mismatch** — wrong spec values, missing env vars
- **Resource issue** — OOM, GPU unavailable, network timeout
- **Logic bug** — wrong output, assertion failure, unexpected state

### Step 4: Fix

Make the minimal change to address the diagnosed issue. Don't fix unrelated things in the same loop iteration.

### Step 5: Re-execute

Go back to Step 1. Same command, same observation method.

## Exit Condition

The loop ends when **success criteria are met**. Report to the user:
- What was executed
- What the outcome was
- Whether success criteria are satisfied

If success criteria aren't defined in the project CLAUDE.md, ask the user what "working" looks like before starting.

## Verification Spectrum (Quick Reference)

**Simplest: local test**
```
run test → read output → fix → rerun
```

**Medium: local service**
```
start → probe → fix → restart
```

**Heaviest: remote job**
```
submit → find pod → tail logs → fix → kill old job → resubmit
```

Match the verification level to the change. Don't submit a remote job when a local test suffices.

## Required Project Info Template

Projects should provide the following in their CLAUDE.md (fill only relevant sections):

```markdown
## Verification

### Execute
- **Test command:** `<how to run tests>`
- **Submit command:** `<how to submit job/deploy>`
- **Start command:** `<how to start local service>`

### Observe
- **Test output:** `<where test results appear>`
- **Log location:** `<log path pattern>`
- **Process discovery:** `<how to find running processes/pods>`
- **Health check:** `<how to check if service is running>`

### Diagnose
- **Signal chain:** `<ordered list of components, check in order>`
- **Common failure patterns:** `<known error → likely cause mapping>`

### Success Criteria
- `<what "working" looks like>`
```
