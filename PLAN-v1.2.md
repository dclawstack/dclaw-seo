# DClaw SEO — v1.2 Feature Roadmap

> Based on: Y Combinator vertical SaaS principles, trending GitHub repos (serp-analyzer, lighthouse-ci), AI product research (SurferSEO, Clearscope, MarketMuse, Frase)

## Pre-Flight Checklist

- [ ] `frontend/package-lock.json` committed after any `npm install` / dependency change
- [ ] `frontend/next-env.d.ts` exists and is committed
- [ ] `docker-compose.yml` healthchecks correct
- [ ] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`

## v1.0 Feature Inventory (Current)

- [ ] Keyword tracking & ranking monitor
- [ ] Site audit (crawl + issues)
- [ ] Content optimization suggestions
- [ ] Dashboard with traffic/visibility metrics
- [ ] Real backend CRUD (no mocks)
- [ ] Docker + Helm deployment
- [ ] Alembic migrations
- [ ] Backend tests

---

## v1.2 Roadmap

### P0 — Must Have (Ship in v1.0, demo-ready)

#### 1. AI SEO Copilot (Content Optimizer)
**Description:** AI assistant that analyzes any page and gives specific optimization recommendations: keyword density, readability, internal links, meta tags, schema markup.
- **AI Angle:** LLM-powered content analysis against SERP top-10. RAG over SEO best practices.
- **Backend:** `/api/v1/ai/optimize` endpoint. Crawl + analyze pipeline.
- **Frontend:** Optimization report with before/after score and actionable checklist.
- **Files:** `backend/app/services/seo_optimizer.py`, `frontend/src/app/optimize/report.tsx`

#### 2. Keyword Research & Clustering
**Description:** Discover keywords, group into topic clusters, estimate difficulty and search volume.
- **AI Angle:** LLM-generated keyword variations. Semantic clustering (embeddings).
- **Backend:** Keyword data API integration (DataForSEO/SerpApi). Clustering algorithm.
- **Frontend:** Keyword explorer with cluster visualization (bubble chart).
- **Files:** `backend/app/services/keyword_research.py`

#### 3. Rank Tracking & SERP Monitoring
**Description:** Track keyword positions daily. Monitor SERP features (featured snippets, people also ask).
- **Backend:** Scheduled rank checks. SERP feature extraction.
- **Frontend:** Rank trend charts. SERP feature timeline.
- **Files:** `backend/app/services/rank_tracker.py`

#### 4. Technical Site Audit
**Description:** Crawl site and identify technical issues: broken links, duplicate content, missing alt text, slow pages, mobile issues.
- **Backend:** Crawler (Scrapy/httpx). Issue classification.
- **Frontend:** Audit report with severity scores and fix instructions.
- **Files:** `backend/app/services/site_auditor.py`

### P1 — Should Have (v1.1–1.2)

#### 5. Competitor Gap Analysis
**Description:** Compare your keyword profile vs competitors. Find keywords they rank for that you don't.
- **Backend:** Competitor domain analysis. Gap detection algorithm.
- **Frontend:** Gap matrix with opportunity scores.

#### 6. AI Content Brief Generator
**Description:** Generate detailed content briefs from a target keyword: outline, questions to answer, recommended length, internal links.
- **AI Angle:** SERP analysis + LLM brief generation.
- **Backend:** `/api/v1/ai/content-brief` endpoint.
- **Frontend:** Brief viewer with export to Google Docs/Notion.

#### 7. Backlink Analysis & Monitoring
**Description:** Track backlinks, anchor text, referring domains. Alert on new/lost links.
- **Backend:** Backlink data API. Change detection.
- **Frontend:** Backlink profile with authority scores.

#### 8. Core Web Vitals & Performance Monitor
**Description:** Track LCP, FID, CLS over time. Get optimization recommendations.
- **Backend:** Lighthouse CI integration. Performance data collection.
- **Frontend:** Performance dashboard with historical trends.

### P2 — Could Have (v1.3+)

#### 9. AI-Generated Meta Tags & Schema
**Description:** Auto-generate optimized title tags, meta descriptions, and JSON-LD schema.

#### 10. Voice Search Optimization
**Description:** Identify and optimize for conversational/voice queries.

#### 11. Local SEO Manager
**Description:** Google Business Profile sync, local citation tracking, review monitoring.

#### 12. Predictive Rank Forecasting
**Description:** AI predicts ranking changes based on content updates and competitor activity.

---

## Implementation Priority

1. **Week 1–2:** AI SEO Copilot (P0.1) + Keyword Research (P0.2)
2. **Week 3–4:** Rank Tracking (P0.3) + Site Audit (P0.4)
3. **Week 5–6:** Competitor Gap (P1.5) + Content Briefs (P1.6)
4. **Week 7–8:** Backlink Analysis (P1.7) + Performance Monitor (P1.8)
