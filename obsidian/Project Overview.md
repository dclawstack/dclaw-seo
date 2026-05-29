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

Design principle: real free data always works; AI enrichment and live SERP positions activate when a provider is configured in `backend/.env` — no fabricated metrics. Phases 2–4 (P1/P2 platform features + hardening: auth, billing, multi-tenant, observability, prod deploy) await go-ahead. See [[Roadmap]] and [[Open Issues]].

## Related

- [[Architecture]]
- [[Roadmap]]
- [[Glossary]]
