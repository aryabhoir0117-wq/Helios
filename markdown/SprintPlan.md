# Project Helios — Sprint Plan (v2 — FastAPI + MongoDB Atlas)

Architecture pivot from the original Bible: **MongoDB Atlas** instead of Postgres/Neon,
**FastAPI** confirmed as backend, developing locally on Windows + Docker Desktop, **Render**
for eventual deployment instead of Oracle Cloud (no card for Oracle signup). Same logical
data model and incident lifecycle as the Bible throughout.

**Target: 40% = Sprint 0 through Sprint 4.**

---

## Sprint 0 — Foundation ✅ DONE
- [x] GitHub repo created & pushed (`aryabhoir0117-wq/Helios`)
- [x] Python venv (`.H`) + FastAPI + Uvicorn installed
- [x] MongoDB Atlas cluster created, connected via Beanie/Motor
- [x] First endpoint (`/health`) running

## Sprint 1 — Core Data Layer + Observe ✅ DONE
- [x] Models: `Server`, `Metric`, `Deployment`, `Incident` (Beanie documents)
- [x] Full CRUD routers for all four, tested via Swagger UI
- [x] `prometheus-fastapi-instrumentator` wired in — FastAPI self-reports metrics
- [x] Prometheus running in Docker, scraping FastAPI (`helios-backend` target UP)
- [x] Live query (`http_requests_total`) confirmed showing real traffic

## Sprint 2 — Container Visibility 
- [x] cAdvisor added to `docker-compose.yml`, scraping container-level CPU/RAM
- [x] Both Prometheus targets (`helios-backend`, `cadvisor`) confirmed UP
- [x] Real container metrics queryable (CPU/memory per container)

## Sprint 3 — Detect Engine
- [x] Background polling task (FastAPI `BackgroundTasks` or APScheduler) reads Prometheus metrics on an interval
- [x] Threshold rules (e.g. CPU > 85% sustained) evaluated against live data
- [x] A breached threshold auto-creates an `Incident` document (status: "open")
- [x] Verify: manually spike CPU in a test container → an incident appears in `/incidents` within the poll interval

## Sprint 4 — Investigate + Explain
- [x] Investigate: rule-based root-cause check — recent `Deployment`? container restart loop? resource exhaustion?
- [x] Incident updated with a `root_cause` field once investigated
- [x] Explain: Groq API call (Gemini fallback) turns root cause into a plain-English summary, stored on the incident
- [x] Verify end-to-end: trigger real load → Detect fires → Investigate attaches cause → Explain adds plain-English text, all visible via `GET /incidents`

---
## Sprint 5 — Predict + Recommend
- [x] Predict: pull recent CPU history for a server (last N minutes of metrics from Prometheus or your `Metric` collection) and do simple trend extrapolation — is usage climbing, flat, or falling? (linear regression or basic slope check is enough, no ML model needed)
- [x] Store prediction on the incident — e.g. `predicted_trend: "rising"` + a plain value like `predicted_cpu_in_10min`
- [x] Recommend: given root_cause + trend, map to a small bounded action set (e.g. "restart container", "scale resources", "monitor only" — no free-form AI-generated actions, keep it deterministic/rule-based like Investigate)
- [x] Store `recommended_action` on the incident
- [x] Verify end-to-end: stress test → incident has root_cause, explanation, predicted_trend, recommended_action, all visible via `GET /incidents`
- [x] Reason Code Refractor Included 

## Sprint 6 — Recover + Verify
- [x] Recover: given `recommended_action` from Sprint 5, execute it for real using the Docker SDK (`docker-py`) — e.g. actually restart the container tied to `server_id`
- [x] Guardrails: only auto-execute for specific safe actions (e.g. "restart container"); anything riskier stays recommendation-only for now (no auto-scaling infra changes, no destructive actions)
- [x] Log the action taken on the incident — `action_taken`, `action_timestamp`, `action_result` ("success"/"failed" + any Docker SDK error message)
- [x] Verify: after executing, re-query Prometheus for that container's CPU a short delay later, compare to the original spike — store `post_action_cpu` and a `resolved: true/false` flag based on whether it dropped back under threshold
- [x] If resolved, auto-update `Incident.status` from `"open"` to `"resolved"`
- [x] Verify end-to-end: stress test → full lifecycle fires → container actually gets restarted → CPU drops → incident auto-closes, all visible via `GET /incidents`

## Remaining 60% (sequenced for later)
- **Sprint 5** — Predict (trend extrapolation) + Recommend (bounded action set)
- **Sprint 6** — Recover (execute real action: restart container via Docker SDK) + Verify (re-check metrics after action)
- **Sprint 7** — Learn + auto-generated post-incident reports
- **Sprint 8** — React + Three.js frontend: 3D server globe, live dashboards
- **Sprint 9** — Time Machine (historical Prometheus queries by time range) + Incident timeline UI
- **Sprint 10** — Incident Simulator panel + one-click Auto Demo Mode
- **Later** — Deploy to Render (or Oracle Cloud if card access appears) for the real public demo

## Winning-condition reminders
- Every demoed feature must be real — no fabricated data, no fake terminals.
- Finish Sprint 0–4 (the "40%") completely before any visual polish.
- 3 pillars fully real beats 5 pillars half-faked.