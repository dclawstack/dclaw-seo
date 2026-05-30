# Project Overview

## What DClaw SEO is

**An AI SEO agent for the DClaw Stack.** It audits sites, researches keywords, optimizes content, and tracks rankings — with an AI Copilot as the first-class entry point (per the DClaw AI-Copilot mandate).

The product targets teams that treat SEO as a measurable growth channel, drawing on the playbooks of Ahrefs, SEMrush, SurferSEO, Clearscope, and MarketMuse. SEO tooling has high willingness-to-pay and clear ROI metrics, which is why it's a DClaw vertical.

## Core value props

- **AI SEO Copilot** — analyse a page/site against the SERP top-10 and return a prioritised, actionable checklist.
- **Keyword research & clustering** — LLM keyword expansion + intent classification + semantic clustering.
- **Content optimization** — readability, keyword-density, and semantic-coverage scoring with concrete fixes.
- **Rank tracking** — daily position checks across engines/locations, with anomaly detection on big drops.

## Maturity

**Phase 1 complete — v1.0 (demo-ready).** All P0 product features shipped end-to-end: the AI Copilot (P0.1) with a provider-swappable LLM layer (P0.0, Ollama/OpenRouter), keyword research on free Google Suggest data + LLM enrichment (P0.2), a real content optimizer (P0.3), rank tracking with drop alerts (P0.4), a live dashboard (P0.5), and a scripted demo flow (P0.6). 23 backend tests green; marketing landing live at **dclaw-seo.vercel.app**.

Design principle: real free data always works; AI enrichment and live SERP positions activate when a provider is configured (in-app **Settings** or `backend/.env`) — no fabricated metrics.

**Phase 2 complete (v1.2).** P1 platform features shipped: real deep-crawl site audit (P1.2), backlink toxicity + new/lost (P1.1), competitor gap analysis (P1.3), AI content briefs (P1.4), and Core Web Vitals via PageSpeed Insights (P1.5). Plus in-app LLM provider configuration running on local Ollama.

**Phase 3 complete (P2 vertical/scale).** AI content writer (P2.1), AI meta tags & JSON-LD schema (P2.2), video SEO (P2.4), local SEO manager — GBP/citations/NAP/reviews (P2.3), white-label PDF/CSV reports with scheduling (P2.5), and predictive rank forecasting (P2.6).

**Phase 4 complete — v2.0 (market-ready).** Hardening + launch shipped: self-contained JWT auth on all feature routes (H.1), org→project multi-tenancy with a per-org LLM cost ledger + cost cap (H.3), Stripe-optional billing (H.2), Prometheus/Grafana observability (H.4), security hardening (H.5, incl. a critical Next.js CVE patch), a production Helm chart with CloudNativePG (H.6), and full docs/demo (H.7). The marketing landing site (H.8) shipped earlier on Vercel.

**🏁 The entire dev plan is complete: 34/34 tasks across all 5 phases.** 92 backend tests green; 11 alembic migrations; live stack at version 2.0.0. The design rule held throughout — real free data always works; AI/provider depth activates when configured; **no fabricated metrics**. See [[Roadmap]], [[Build Log]], and [[Open Issues]].

## Related

- [[Architecture]]
- [[Roadmap]]
- [[Glossary]]
