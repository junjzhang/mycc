---
name: upstream-bug-report
description: >-
  Convert local debugging results into high-quality upstream issues or RFC
  comments. Use when filing bugs to external projects with clear reproduction,
  first-failure evidence, root-cause hypothesis, and scoped fix suggestions.
---

# Upstream Bug Report

## Purpose

Turn internal debugging output into an actionable upstream issue with minimal maintainer back-and-forth.

## When to Use

Use this skill when:
- Root cause appears to be in external dependency behavior
- You have a local workaround but need upstream fix
- You are filing a new issue or commenting on an existing RFC/issue

## Before Writing

1. **Search for existing issues first.** Run `gh search issues --repo {owner}/{repo} "<key error or behavior>"` to check for duplicates. If a similar issue exists, comment on it instead of filing a new one.
2. **Check the upstream repo's issue template.** Run `gh api repos/{owner}/{repo}/contents/.github/ISSUE_TEMPLATE` or browse the repo's `.github/ISSUE_TEMPLATE/` directory. If a bug report template exists, follow its structure instead of the reference sections below.
3. **Sanitize internal details.** Remove all references to internal software, proprietary infra, private repo names, API keys, secrets, and credentials. Use generic terms (e.g. "online weight update" not "TensorBus sync").

## Reference Sections (use as needed, or follow upstream template)

1. **Environment** — exact versions, topology, reproducibility on latest
2. **Minimal Reproduction** — short deterministic steps, timing notes if race-dependent
3. **Expected vs Actual** — one sentence each, precise and falsifiable
4. **First-Failure Evidence** — earliest error (timestamp + component), key stack frame, distinguish from cascades
5. **Root-Cause Hypothesis** — specific state transition or API contract mismatch, exact code location(s)
6. **Suggested Fix Direction** — minimal guard/change, why safe, scope and non-goals
7. **Mitigation / Workaround** — current operational mitigation, tradeoffs

## Quality Bar

- Title contains behavior + trigger + impact
- Repro is short and readable
- Root cause clearly separated from cascades
- Includes one concrete patch sketch or pseudocode
- Avoids over-claiming coverage

## Comment Template (Short)

```text
This looks related to issue #X. We reproduced a race where <event A> can occur
after <pause/ack point>, causing <collective mismatch/timeout>. First failure is
in <component> at <time>, while later watchdog errors are cascades. A minimal fix
appears to be <guard/condition>. Happy to share logs or test patch.
```

## Output Contract

Return:
1. Ready-to-submit issue body
2. Optional short cross-link comment for related RFC/issue threads
