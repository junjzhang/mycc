---
name: swanlab
description: >-
  Query SwanLab experiment metrics and run status.
  Use when checking training/producer metrics, comparing runs, or investigating experiment health.
  Keywords: swanlab, metrics, experiment, loss, reward, training progress, wandb.
---

# SwanLab

Query experiment metrics from SwanLab. All commands run via `pixi run -e dev python3 -c "..."`.

## Authentication

Already configured. Default workspace: `junjayzhang`, project: `dev`.

## Quick Reference

### List runs

```python
import swanlab
api = swanlab.Api()

# All running experiments
for r in api.runs(path='junjayzhang/dev', filters={'state': 'RUNNING'}):
    print(f'{r.name} | {r.id} | {r.state} | {r.created_at}')

# Filter by state: RUNNING, FINISHED, CRASHED, ABORTED
```

### Get metrics from a run

```python
run = api.run(path='junjayzhang/dev/<experiment_id>')
df = run.metrics(keys=['<metric_key>'], sample=50)  # returns pandas DataFrame
```

### Known metric keys

**Producer runs** (`*_producer`):
- `group/reward_mean`, `group/reward_min`, `group/reward_max`
- `group/n_truncated`, `group/truncated_ratio`
- `group/n_non_truncated`, `group/success_ratio`
- `group/length_mean`, `group/length_min`, `group/length_max`
- `group/output_tokens_mean`, `group/output_tokens_max`
- `group/python_calls_mean`, `group/python_errors_total`
- `group/n_context_exhausted`, `group/n_max_turns`

**Train runs** (`*_train`):
- `loss_metrics/global_avg_loss`, `loss_metrics/global_max_loss`
- `time_metrics/end_to_end(s)`, `time_metrics/data_loading(s)`, `time_metrics/data_loading(%)`
- `optimization/learning_rate` (or `optimization/scheduler_0/learning_rate`)

### Run properties

```python
run.name          # str
run.id            # experiment_id
run.state         # RUNNING | FINISHED | CRASHED | ABORTED
run.created_at    # ISO 8601
run.url           # web UI link
```

## Usage Pattern

When asked to check experiment metrics or training progress, use this skill to:

1. List runs to find the relevant experiment ID
2. Fetch specific metrics with `run.metrics(keys=[...], sample=N)`
3. Report trends (is loss decreasing? is truncation ratio increasing? etc.)

Always wrap API calls in `pixi run -e dev python3 -c "..."` since swanlab is only in the dev environment.
