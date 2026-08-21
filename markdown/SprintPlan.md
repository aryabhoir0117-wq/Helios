# Project Helios — Sprint Plan (v2 — FastAPI + MongoDB Atlas)

Architecture pivot from the original Bible: **MongoDB Atlas** instead of Postgres/Neon,
**FastAPI** confirmed as backend, developing locally on Windows + Docker Desktop, **Render**
for eventual deployment instead of Oracle Cloud (no card for Oracle signup). Same logical
data model and incident lifecycle as the Bible throughout.

**Target: 40% = Sprint 0 through Sprint 4.**

---

## Sprint 0 — Foundation 🔪 DONE
- [x] GitHub repo created & pushed (`aryabhoir0117-wq/Helios`)
- [x] Python venv (`.H`) + FastAPI + Uvicorn installed
- [x] MongoDB Atlas cluster created, connected via Beanie/Motor
- [x] First endpoint (`/health`) running

## Sprint 1 — Core Data Layer + Observe 🔪 DONE
- [x] Models: `Server`, `Metric`, `Deployment`, `Incident` (Beanie documents)
- [x] Full CRUD routers for all four, tested via Swagger UI
- [x] `prometheus-fastapi-instrumentator` wired in — FastAPI self-reports metrics
- [x] Prometheus running in Docker, scraping FastAPI (`helios-backend` target UP)
- [x] Live query (`http_requests_total`) confirmed showing real traffic

## Sprint 2 — Container Visibility 🔪 DONE
- [x] cAdvisor added to `docker-compose.yml`, scraping container-level CPU/RAM
- [x] Both Prometheus targets (`helios-backend`, `cadvisor`) confirmed UP
- [x] Real container metrics queryable (CPU/memory per container)

## Sprint 3 — Detect Engine 🔪 DONE
- [x] Background polling task (FastAPI `BackgroundTasks` or APScheduler) reads Prometheus metrics on an interval
- [x] Threshold rules (e.g. CPU > 85% sustained) evaluated against live data
- [x] A breached threshold auto-creates an `Incident` document (status: "open")
- [x] Verify: manually spike CPU in a test container → an incident appears in `/incidents` within the poll interval

## Sprint 4 — Investigate + Explain 🔪 DONE
- [x] Investigate: rule-based root-cause check — recent `Deployment`? container restart loop? resource exhaustion?
- [x] Incident updated with a `root_cause` field once investigated
- [x] Explain: Groq API call (Gemini fallback) turns root cause into a plain-English summary, stored on the incident
- [x] Verify end-to-end: trigger real load → Detect fires → Investigate attaches cause → Explain adds plain-English text, all visible via `GET /incidents`

---
## Sprint 5 — Predict + Recommend 🔪 DONE
- [x] Predict: pull recent CPU history for a server (last N minutes of metrics from Prometheus or your `Metric` collection) and do simple trend extrapolation — is usage climbing, flat, or falling? (linear regression or basic slope check is enough, no ML model needed)
- [x] Store prediction on the incident — e.g. `predicted_trend: "rising"` + a plain value like `predicted_cpu_in_10min`
- [x] Recommend: given root_cause + trend, map to a small bounded action set (e.g. "restart container", "scale resources", "monitor only" — no free-form AI-generated actions, keep it deterministic/rule-based like Investigate)
- [x] Store `recommended_action` on the incident
- [x] Verify end-to-end: stress test → incident has root_cause, explanation, predicted_trend, recommended_action, all visible via `GET /incidents`
- [x] Reason Code Refractor Included 

## Sprint 6 — Recover + Verify 🔪 DONE
- [x] Recover: given `recommended_action` from Sprint 5, execute it for real using the Docker SDK (`docker-py`) — e.g. actually restart the container tied to `server_id`
- [x] Guardrails: only auto-execute for specific safe actions (e.g. "restart container"); anything riskier stays recommendation-only for now (no auto-scaling infra changes, no destructive actions)
- [x] Log the action taken on the incident — `action_taken`, `action_timestamp`, `action_result` ("success"/"failed" + any Docker SDK error message)
- [x] Verify: after executing, re-query Prometheus for that container's CPU a short delay later, compare to the original spike — store `post_action_cpu` and a `resolved: true/false` flag based on whether it dropped back under threshold
- [x] If resolved, auto-update `Incident.status` from `"open"` to `"resolved"`
- [x] Verify end-to-end: stress test → full lifecycle fires → container actually gets restarted → CPU drops → incident auto-closes, all visible via `GET /incidents`

## Sprint 7 — Learn + Reports 🔪 DONE
- [x] Incident history query: pull all resolved incidents for a given `server_id`, sorted oldest → newest
- [X] Pattern summary: restart success rate, most common `root_cause`, average time-to-resolve, recurrence count — via `GET /incidents/servers/{server_id}/insights`
- [x] Post-incident report generation: once `resolved: true`, auto-generate a plain-English report (Groq/Gemini, same pattern as `explanation.py`) and store it as `post_incident_report`
- [x] New endpoint: `GET /incidents/{id}/report` to view a single incident's report
- [x] Verify end-to-end: resolve an incident → report auto-generates and reads sensibly → insights endpoint reflects real incident history

## Sprint 8.1 — Frontend Scaffold 🔪 DONE
- [x] Init `/frontend` with Vite + React
- [x] Install and configure Tailwind
- [x] Install Three.js (+ `@react-three/fiber` and `@react-three/drei` if going the React-Three ecosystem route rather than raw Three.js)
- [x] Install React Router for page navigation (Index, Login, Dashboard, Globe, Incidents, Servers, Reports, Settings as route stubs)
- [x] Set up `.env` for frontend (API base URL) + confirm CORS is enabled on the FastAPI side so `/frontend` can actually call `localhost:8000`
- [x] Sanity check: a stub page successfully fetches and displays something real from `GET /health` or `GET /servers`

Cloud Migration Work 
## Sprint 8.1a — Codespaces Setup (today, ~30 min)
- [x]Create Codespace on aryabhoir0117-wq/Helios
 Set up venv, pip install -r requirements.txt inside it
- []Add .env secrets (MONGO_URI, GROQ_API_KEY, GEMINI_API_KEY)
- []Verify python and docker both work inside the Codespace terminal
## Sprint 8.1b — Move the Observe Stack (~20 min)
- []docker compose up -d inside Codespace (Prometheus + cAdvisor)
- [ ]Confirm both targets show "UP" at the forwarded Prometheus port (9090)
## Sprint 8.1c — Move Test Load (~15 min)
- []Start server-1-cpu, server-2-mem, server-3-idle inside the Codespace- [x]Confirm docker ps shows all three running there, not locally
## Sprint 8.1d — Move the Backend (~15 min)
- []uvicorn main:app --host 0.0.0.0 --port 8000 inside Codespace
- []Forward port 8000, confirm /docs loads from your normal browser
## Sprint 8.1e — End-to-End Verify (~15 min)
- []Register the 3 servers via forwarded Swagger UI
 Wait for incidents (CPU + memory) to appear via GET /incidents
- []Trigger recovery on one, confirm it resolves — all from your browser, zero local load
## Sprint 8.1f — Automate it (optional, later)
- []- [x] Write a .devcontainer/devcontainer.json so a fresh Codespace auto-installs deps and starts services on open, instead of manual steps each time
## Sprint 8.1g — Deploy Backend to Render (~30-45 min)
- [] Create a Render Web Service pointing at aryabhoir0117-wq/Helios
- [] Set build command (pip install -r requirements.txt) and start command (uvicorn main:app --host 0.0.0.0 --port $PORT)
- [] Add the same env vars (MONGO_URI, GROQ_API_KEY, GEMINI_API_KEY) in Render's dashboard
- [] Confirm /health and /docs load at your public Render URL
## Sprint 8.2 — Index / Landing Page
- [x] Hero section: product name, tagline, "what Helios does" (Observe → Detect → Investigate → Explain → Recover, matching your own doc's framing)
- [x] Interactive element(s) — this is the one page that's pure storytelling, not real data, so this is where animation/motion budget goes
- [x] CTA into Login
- [x] Placeholder for your logo once it's done

## Sprint 8.3 — Login
- [ ] Email/password form (visual + basic validation, since you're not building a real user table/roles system yet)
- [ ] Google OAuth sign-in (real, via Google's OAuth flow)
- [ ] GitHub OAuth sign-in (real, via GitHub's OAuth flow)
- [ ] Decide + implement how a successful login is tracked on the frontend (session/token storage) even if there's no backend user/session model behind it yet
- [ ] Loading/connection-check screen after login, with a custom spinner/animation

## Sprint 8.4 — Dashboard + Globe (core)
- [ ] Three.js rotating globe, server nodes plotted on it
- [ ] Color-coded nodes by status (healthy/warning/critical), pulled from real `/servers` + `/metrics` data
- [ ] Click-to-zoom on a node → shows that server's live stats
- [ ] Dashboard shell around the globe: health score, active incident count, CPU/RAM averages, AI summary line — wired to real backend data

## Sprint 8.5 — Incident Center
- [ ] Card-based incident list (status, severity, assigned)
- [ ] Incident detail view: root cause, explanation, timeline, wired to existing `/incidents` data

## Sprint 8.6 — Recovery + Reports
- [ ] Restart button wired to real `POST /incidents/{id}/recover`
- [ ] Rollback/Scale buttons present but visually marked "coming soon" (no backend for these yet)
- [ ] Reports view pulling from `/insights` and `/report`

## Sprint 11 — Sandbox Mode + Super Admin (referred, after frontend)
- [ ] Sandbox Mode: auto-dockerization on git push, aimed at making the whole loop approachable for beginners without manual Docker setup
- [ ] Super Admin role/console: manage users, organizations, config — scoped down from the full enterprise doc to whatever's realistic for a portfolio project


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