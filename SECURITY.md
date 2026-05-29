# Security (H.5)

How DClaw SEO handles secrets, containers, transport, and dependency hygiene.

## Secrets

- **No secrets in the repo.** All credentials come from the environment
  (`backend/.env`, gitignored) or, in Kubernetes, from a `Secret` (see
  `helm/`). `.env.example` documents every key with empty/placeholder values.
- `SECRET_KEY` signs JWTs. It defaults to a dev placeholder; **set a strong
  random value in production** (`openssl rand -hex 32`). The app logs a warning
  on startup if the default is used outside `dev`.
- Third-party keys (`OPENROUTER_API_KEY`, `STRIPE_API_KEY`, `GBP_API_KEY`,
  `PAGESPEED_API_KEY`, SMTP) are all optional and read from env only.

## Containers

- **Backend** runs as the non-root `appuser` (see `backend/Dockerfile`).
- **Frontend** runs as the non-root `node` user (see `frontend/Dockerfile`).
- Kubernetes deployments set `runAsNonRoot: true` and drop capabilities (see
  `helm/`).

## Transport

- TLS is terminated at the ingress. The Helm chart ships an `Ingress` with TLS
  enabled and HSTS; the app also emits HSTS + hardening headers
  (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`,
  `Permissions-Policy`) via middleware in production.

## AuthN / AuthZ

- All feature APIs require a valid JWT (`Authorization: Bearer …`); only
  `/health`, `/metrics`, `/admin/health`, and `/api/v1/auth/*` are public.
- Passwords are hashed with bcrypt; tokens are HS256 with a configurable expiry.
- Data and LLM spend are scoped per organization (multi-tenant, see H.3).

## Dependency audit

Run the dependency vulnerability scan locally:

```bash
./scripts/security_audit.sh
```

CI runs `pip-audit` on every push (non-blocking, see `.github/workflows/ci.yml`).
