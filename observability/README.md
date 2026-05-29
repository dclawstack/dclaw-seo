# Observability (H.4)

The backend exposes Prometheus metrics and health endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness (used by container/K8s liveness probe) |
| `GET /admin/health` | Readiness — DB connectivity + LLM configuration |
| `GET /metrics` | Prometheus exposition (request count + latency histograms) |

Metrics emitted (labels in parentheses):

- `dclaw_seo_http_requests_total` (method, path, status)
- `dclaw_seo_http_request_duration_seconds` histogram (method, path)

`path` uses the matched **route template** (e.g. `/api/v1/seo/audit`), so per-id
URLs never blow up cardinality.

## Run the stack

```bash
docker compose -f observability/docker-compose.observability.yml up -d
```

- Grafana → http://localhost:3030 (admin/admin) — the **DClaw SEO — Service
  Overview** dashboard is auto-provisioned.
- Prometheus → http://localhost:9090

Prometheus scrapes the backend at `host.docker.internal:8095/metrics`; make sure
the app stack is running (`docker compose -f docker-compose.standalone.yml up -d`).
