"""Prometheus metrics + request-timing middleware.

Exposes counters/histograms for HTTP traffic and a helper to render the
exposition format for ``GET /metrics``. The path label uses the matched route
template (e.g. ``/api/v1/seo/audit``) — not the raw URL — so high-cardinality
ids never explode the metric space.
"""

from __future__ import annotations

import time

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

REQUEST_COUNT = Counter(
    "dclaw_seo_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "dclaw_seo_http_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["method", "path"],
)


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        path = _route_template(request)
        if path != "/metrics":  # don't measure the scrape endpoint itself
            REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
            REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
        return response


def metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
