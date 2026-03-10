---
name: diagnose-bug
description: Hypothesis-first bug diagnosis. Verify the user's diagnosis before proposing alternatives. Keywords: bug, diagnose, debug, fix, hypothesis, root cause, crash, error, timeout, traceback.
---

# Diagnose Bug

Structured debugging workflow that respects the user's diagnosis.

## Usage

```
/diagnose-bug <error message>
Hypothesis: <your diagnosis>
Check: <specific file/function to verify>
```

## Workflow

1. **Verify the user's hypothesis FIRST.** Read the specified file/function, check git history, trace the code path. Do not propose alternative theories until the hypothesis is confirmed or ruled out.

2. **If confirmed:** Implement the minimal fix. No refactoring, no cleanup, no "while we're here" improvements.

3. **If ruled out:** Explain concretely why (show the code path that contradicts it), then propose ONE alternative hypothesis and verify it the same way.

4. **Never skip straight to a fix** without showing evidence that the root cause is understood.
