---
name: weekly-report
description: >-
  Generate a weekly report summarizing commits and PRs across the main repo
  and all external/ submodules. Keywords: weekly report, 周报, work summary, 工作总结.
---

# Weekly Report

Generate a structured work summary from git history, covering the main repo and all external/ submodules.

## When to Use

- User asks for a "周报", "weekly report", "work summary"
- User wants to summarize their commits/PRs over a date range

## Data Collection

1. **Identify the user**: `git log --format="%ae" -1` to get the author email
2. **List submodules**: `ls external/` to find all submodule repos
3. **Collect commits** for each repo (main + each external/ submodule):
   ```bash
   git log --author="<user>" --since="<start-date>" --format="%h %as %s" --reverse
   ```
4. **Collect PRs** for each repo:
   ```bash
   gh pr list --author="@me" --state=all --limit=100 --json number,title,state,createdAt | \
     python3 -c "import json,sys; [print(f'{p[\"title\"]} ({p[\"createdAt\"][:10]})') for p in sorted(json.load(sys.stdin), key=lambda x: x['createdAt']) if p['createdAt'] >= '<start-date>']"
   ```

## User Preferences (IMPORTANT)

- **不要包含具体的 PR / issue 编号**：不出现 `#123` 这类引用
- **必须有主线**：所有工作围绕一条核心叙事线串联，而非孤立罗列。根据实际工作内容提炼主线（例如"围绕 X 模型在 Y 场景的 RL 训练"）
- **涵盖所有 external/ 子模块**（除 vllm 外），只包含用户参与的 commit
- **不要产出统计**：末尾不加 "X commits / Y PRs" 之类的数字汇总
- **专业感与工作量**：适当展开描述技术细节，体现深度，避免过于简略
- **ASCII 架构图**：在关键架构点插入 ASCII 图（2-4 处即可，不要过多），帮助读者快速理解系统设计

## Document Structure

```markdown
# <Project> 工作总结

> <date-range>
>
> 主线：<一句话概括所有工作的核心叙事线>

---

## 一、<模块/主题>
- 要点描述，展开技术细节
- ASCII 图（如适用）

## 二、<模块/主题>
...
```

### Organizing Principles

1. **按技术模块/主题分节**，不按时间排列
2. **每节描述与主线关联**：说明该模块工作为何服务于主线目标
3. **稳定性/Bug 修复单独成节**：体现生产环境实战经验
4. **基础设施重构单独成节**：体现工程质量投入
5. **可观测性与文档**可合并为一节

## Output

Write the report to `weekly_report_<start>_<end>.md` in the project root.
