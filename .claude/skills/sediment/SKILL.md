---
name: sediment
description: >-
  Capture reusable knowledge after milestones. Systematically review what was
  learned and persist it to the right layer. Keywords: sediment, crystallize,
  capture, persist, remember, learned, milestone, retrospective.
---

# Sediment

Persist valuable, reusable knowledge to the right layer after completing a task or milestone.

## When to Use

- After fixing a non-trivial bug (root cause pattern worth remembering)
- After a design decision that affects future work
- After discovering an undocumented behavior in a dependency
- After establishing a new workflow or convention
- When the user explicitly asks to sediment/capture/remember

## Workflow

### 1. Identify what's worth keeping

Ask: is this **stable, reusable, and verified**? If it's speculative or session-specific, skip it.

### 2. Check for stale entries

Before writing new entries, scan existing memory, skills, rules, and CLAUDE.md for anything this session **invalidated or superseded**. Update or delete stale entries first.

### 3. Route to the right layer

| What | Where | Example |
|---|---|---|
| Project-specific facts, known bugs, debugging notes | `memory/MEMORY.md` or topic files | "vLLM START_DP_WAVE race condition" |
| Reusable workflow (multi-step, invoked on demand) | `~/.claude/skills/{name}/SKILL.md` | `/diagnose-bug`, `/upstream-bug-report` |
| Code style / conventions (file-type scoped) | `~/.claude/rules/{name}.md` | Python style, shell rules |
| Cross-project principles / persona / workflow rules | `~/.claude/CLAUDE.md` | "Keep observations in sync" |
| Project architecture, design patterns, verification | `{project}/CLAUDE.md` | Architecture diagrams, test commands |

### 4. Write concisely

- Memory: facts, not narratives
- Skills: actionable steps, not essays
- Rules: short, scoped, triggered by file pattern
- CLAUDE.md: one bullet per rule

## Anti-patterns

- Don't sediment session-specific context (current task, in-progress work)
- Don't duplicate what's already captured elsewhere
- Don't sediment unverified hypotheses — wait until confirmed
