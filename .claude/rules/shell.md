---
paths:
  - "**/*.sh"
---

# Shell Script Rules

- Always start with `set -euo pipefail`
- **Env isolation:** `launch.sh` exports are inherited by ALL subprocesses (Ray head → workers). Process-specific env vars (e.g. NCCL tuning) must NOT be exported in launch.sh — pass them via process-level mechanisms instead.
- Quote all variable expansions: `"$VAR"` not `$VAR`
- Use `#!/usr/bin/env bash` shebang
