# Deploying DClaw SEO to Kubernetes (H.6)

The `dclaw-seo` Helm chart deploys the backend + frontend as `ClusterIP`
services behind an nginx Ingress (TLS via cert-manager), with Postgres managed
by **CloudNativePG**.

## Prerequisites

- A cluster with the [CloudNativePG operator](https://cloudnative-pg.io/) and an
  ingress-nginx + cert-manager install.
- Images published to `ghcr.io/dclawstack/dclaw-seo-{backend,frontend}` (the
  Build workflows do this on push to `main`).

## Install / upgrade

```bash
helm upgrade --install dclaw-seo helm/dclaw-seo \
  --namespace dclaw-seo --create-namespace \
  -f helm/dclaw-seo/values-production.yaml \
  --set image.tag=<git-sha> \
  --set secrets.secretKey=<random> \
  --set postgresql.password=<random>
```

Per-env overlays: `values-staging.yaml`, `values-production.yaml`. **Never**
commit real secrets — pass them via `--set`, a sealed secret, or an external
secrets operator.

## What gets created

- `…-backend` Deployment + ClusterIP Service (probes: `/health`, `/admin/health`;
  Prometheus scrape annotations on `/metrics`).
- `…-frontend` Deployment + ClusterIP Service.
- `…-db` CloudNativePG `Cluster` (bootstraps the `dclaw_seo` DB with the
  chart-managed credentials, exposed at `…-db-rw:5432`).
- `…-env` + `…-db-creds` Secrets, a ServiceAccount, and an Ingress routing
  `/api` + `/health` → backend and `/` → frontend.

All pods run non-root with `RuntimeDefault` seccomp and all capabilities dropped.

## CI

`.github/workflows/deploy.yml` runs `helm lint` + `helm template` on every
post-build trigger (no cluster needed) and performs a real `helm upgrade
--install` only when a `KUBE_CONFIG` secret is configured.
