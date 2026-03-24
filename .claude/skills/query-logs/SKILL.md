---
name: query-logs
description: >-
  Query pod logs via Victoria Logs API. Use when checking remote job logs,
  debugging errors, or searching for specific log patterns across K8s pods.
  Keywords: logs, query logs, victoria logs, check logs, pod logs, search logs.
---

# Query Logs via Victoria Logs

Query K8s pod logs through the Victoria Logs HTTP API at `https://vlcluster.log.dist.systems/select/logsql/query`.

## Composing a Query

Every query starts by **scoping** (which pods), then **filtering** (what content).

### Step 1: Scope — identify the pods

You always need the namespace and at least one pod identifier. Get them from the job context:

```bash
kubectl get pods -o wide | grep <job-prefix>
```

Then scope by one of:
- **Pod IP**: `kubernetes.pod_ip:"10.60.32.9"` — most precise, one pod
- **Pod name prefix**: `kubernetes.pod_name:"slurm-profile-slurm-xx5wq*"` — all pods in a job
- **Node**: `kubernetes.host:"node009"` — everything on a node

Always include namespace: `kubernetes.namespace_name:"user-junjzhang"`

### Step 2: Filter — what you're looking for

Combine with implicit AND (space), explicit `OR`, and `NOT`:

```
_msg:"error" OR _msg:"Traceback"       # match either
_msg:"Loading" NOT _msg:"state-dump"   # match one, exclude other
```

### Step 3: Time range and limit

Set `start`, `end` (ISO8601), and `limit` as URL params. Get job start time from `kubectl get pods` or slurm logs. Default to a 1-3h window around the event of interest.

### Putting it together

```bash
curl -s 'https://vlcluster.log.dist.systems/select/logsql/query?query=<URL-ENCODED-LOGSQL>&limit=50&start=<START>Z&end=<END>Z'
```

URL-encode: `%3A` for `:`, `%22` for `"`, `+` for space.

### Parsing the response

Response is JSONL. Key fields: `_time`, `_msg`, `kubernetes.pod_name`, `kubernetes.host`.

```bash
| python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        d = json.loads(line)
        print(d.get('_time','')[:19], d.get('_msg','')[:200])
    except: pass
" | sort
```

## Querying dmesg / Kernel Logs

dmesg logs use a **different schema** — no `kubernetes.*` fields. Filter by `hostname` and `log_source` instead:

```
hostname:"node013" log_source:"dmesg"
```

Common dmesg queries:
- **OOM kill**: `log_source:"dmesg" _msg:"oom-kill"` or `_msg:"Killed process"`
- **Kernel errors on a node**: `hostname:"node013" log_source:"dmesg"`

Key fields in dmesg entries: `hostname`, `log_source` ("dmesg"), `SYSLOG_IDENTIFIER` ("kernel"), `TRANSPORT` ("kernel").

To find a pod's hostname: query a known pod log entry and read the `kubernetes.host` field.

## When to Prefer This Over kubectl logs

- Pod already terminated — kubectl may not have logs
- Need to search across multiple pods in one query
- Need time-range or content filtering on large logs
- User shares a Victoria Logs UI URL (UI is SPA, use API instead)
