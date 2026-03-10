---
paths:
  - "**/*.py"
---

# Python Code Style

- **Ruff** for linting and formatting, 120-char line length
- **Google-style** docstrings
- **Length-sorted** imports, combine-as-imports
- **PEP 585** type hints (use `list[int]` not `List[int]`)
- **Never use PEP 563** (`from __future__ import annotations`) — it breaks Pydantic and runtime type introspection
- **4-space** indentation
- Run `ruff format` and `ruff check` before committing
