# DClaw SEO — User Guide (v2.0)

**Rank higher with AI.** DClaw SEO is an AI-native SEO platform: audit sites,
research keywords, generate and optimize content, track and forecast rankings,
manage local SEO, and ship white-label reports — with an AI Copilot on every
page. Every AI feature runs on a configurable LLM (local Ollama by default) and
**never fabricates data**: when a provider or key is missing, the feature falls
back to real free-data sources or clearly-labeled deterministic output.

---

## 1. Getting started

1. **Sign up.** Open the app, choose **Create account**, and register with an
   email, password, and organization name. You're issued a session token and
   land on the Dashboard.
2. **Configure your LLM (optional).** Go to **Settings** to point the app at a
   local Ollama instance or an OpenRouter key. Without one, AI features still
   return useful, clearly-labeled results from real free data.
3. **Add a project** under **Account** to organize work by site.

All feature APIs require sign-in; your data and LLM spend are isolated per
organization.

---

## 2. Core SEO tools

| Page | What it does |
|------|--------------|
| **Dashboard** | Visibility/activity summary backed by real counts. |
| **Audit** | Deep technical crawl — 50+ issue types with AI-prioritized fixes. |
| **Keywords** | Long-tail expansion (Google Suggest) + AI intent/clustering. |
| **Content** | Score content 0–100 on readability, density, coverage. |
| **Rankings** | Record positions, detect >5-place drops, view trends. |
| **Backlinks** | Toxicity scoring, new/lost detection. |
| **Competitor** | Keyword/content gap analysis vs a competitor. |
| **Content Brief** | SERP-aware outline, questions, length, secondary keywords. |
| **Performance** | Core Web Vitals (LCP/INP/CLS) via PageSpeed Insights. |

## 3. AI content suite

- **AI Writer** (`/writer`) — long-form article drafts with an originality
  check and LLM fact-check notes.
- **Meta & Schema** (`/meta`) — optimized title/meta tags, Open Graph + Twitter
  cards, and JSON-LD schema for any URL or pasted content.
- **Video SEO** (`/video`) — three CTR-tuned YouTube title variants, a
  description, tags, and hashtags.

## 4. Local SEO (`/local`)

Register a business with its canonical NAP (Name/Address/Phone), then:
- Add directory **citations** (Yelp, YellowPages, …).
- Run a **NAP consistency scan** — normalized comparison flags exact mismatched
  fields and scores consistency.
- Log **reviews** and get an AI-drafted response for each.
- With `GBP_API_KEY` set, sync directly from Google Business Profile.

## 5. Forecasting & reports

- **Forecast** (`/forecast`) — projects future rank positions from your real
  rank history (least-squares trend, competitor-adjusted). Needs ≥2 recorded
  checks; otherwise it says so rather than guessing.
- **Reports** (`/reports`) — branded **PDF/CSV** from your real metrics with an
  AI executive summary. Schedule recurring delivery (email activates when SMTP
  is configured; reports always generate).

## 6. Account, billing & cost control

- **Account** (`/account`) — org details, projects, and the **LLM cost ledger**:
  every AI call is metered (tokens + cost). Set a **monthly cost cap**; once hit,
  AI calls return a clear "cap reached" message.
- **Billing** (`/billing`) — choose Free / Starter / Pro; preview an invoice
  computed from your plan, seats, and metered usage. Connect Stripe with
  `STRIPE_API_KEY` (local invoicing works without it).

## 7. The AI Copilot

The floating Copilot is available on every page. Give it a URL and it fetches
the page, evaluates on-page signals against SEO best practices, and returns
**prioritized next actions** — not just answers.

## 8. Operations

- **Health:** `GET /health` (liveness), `GET /admin/health` (readiness: DB +
  LLM).
- **Metrics:** `GET /metrics` (Prometheus). A Grafana dashboard is provided in
  `observability/`.
- **Deploy:** production Helm chart in `helm/dclaw-seo` (CloudNativePG, TLS
  ingress, non-root pods). See `helm/README.md`.
- **Security:** see `SECURITY.md` (JWT auth, bcrypt, non-root containers, no
  hardcoded secrets, dependency audit).

---

*A printable version of this guide is at `docs/USER_GUIDE.pdf`
(regenerate with `python scripts/build_user_guide_pdf.py`).*
