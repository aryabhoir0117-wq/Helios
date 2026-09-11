## HELIOS 
Project Helios is being developed using FastAPI and MongoDB Atlas. The backend is developed locally on Windows using Docker Desktop. Codespaces is being used for cloud-based development and testing, and Render will be used for deployment.
### Lifecycle of Helios 
observe --> Detect --> Investigate --> Explain --> Predict --> Recommend --> Decision --> Recover --> Verify --> Learn --> Report 
## sprint 0
GitHub repository created and pushed.
Python virtual environment created.
FastAPI and Uvicorn installed.
MongoDB Atlas cluster created and connected using Beanie/Motor.
/health endpoint created and tested.
## sprint 01
Created Beanie models for Server, Metric, Deployment and Incident.
Added CRUD APIs for all four models.
Tested the APIs using Swagger UI.
Added Prometheus instrumentation to FastAPI.
Added Prometheus using Docker.
Connected Prometheus with the FastAPI application.
Verified that real HTTP request metrics are being collected.
## sprint 02
Added cAdvisor to Docker Compose.
Connected cAdvisor with Prometheus.
Verified that both FastAPI and cAdvisor targets are running.
Confirmed that CPU and memory metrics can be collected for containers.
## sprint 03
Added background polling to regularly check Prometheus metrics.
Added threshold-based rules such as CPU usage above 85%.
Created an Incident automatically when a threshold is exceeded.
Tested the system by increasing CPU usage in a test container.
Verified that an incident is created through the /incidents API.
## sprint 04
Added rule-based root cause investigation.
Checks include recent deployments, container restart loops and resource exhaustion.
Added the root_cause field to incidents.
Added Groq API integration for generating a simple explanation.
Added Gemini as a fallback.
Stored the generated explanation in the incident.
Tested the complete flow from detection to explanation.
## sprint 05
Added CPU history analysis using recent Prometheus metrics.
Added basic trend detection using slope or linear regression.
Added predicted CPU usage for the next few minutes.
Added predicted_trend to incidents.
Added a fixed set of recommended actions.
Examples include restarting a container, increasing resources or monitoring the server.
Recommendations are rule-based instead of being generated freely by AI.
Added reason codes as part of the refactoring.
Tested the complete flow with a stress test.
## sprint 06
Added Docker SDK integration using docker-py.
Added automatic execution for safe actions such as restarting a container.
Riskier actions such as scaling resources are still recommendation-only.
Added action details to the incident:
action_taken
action_timestamp
action_result
After recovery, Prometheus is queried again to check CPU usage.
Added post_action_cpu.
Added a resolved field.
Automatically changes the incident status to resolved when the problem is fixed.
Tested the complete recovery process using a stressed container.
## sprint 07
Added incident history for individual servers.
Added server-level incident insights.
Insights include:
Restart success rate
Most common root cause
Average time to resolve
Number of recurring incidents
Added automatic post-incident report generation using Groq/Gemini.
Added post_incident_report to incidents.
Added GET /incidents/{id}/report.
Tested the report generation and insights using actual incident data.

Cloud Data Monitoring 
Codespace shifted 
./start.sh (script written where that manually everytime i dont have to do this steps after opening codespace. 

python3 -m venv .H
source .H/bin/activate
pip install -r requirements.txt

Step 4 — Verify secrets came through automatically:

bash
echo $MONGO_URI

(Should print your actual Mongo connection string, not blank — if blank, we'll troubleshoot that separately)

Step 5 — Start Docker stack:

bash
docker compose up -d
docker ps

(Should show helios-prometheus and helios-cadvisor running)

Step 6 — Start uvicorn:

bash
uvicorn main:app --host 0.0.0.0 --port 8000)
## Frontend 
Frontend Setup
Created the /frontend directory using Vite and React.
Installed and configured Tailwind CSS.
Installed Three.js and React Three Fiber/Drei.
Added React Router.
Created routes for:
Landing page
Login
Dashboard
Globe
Incidents
Servers
Reports
Settings
Added frontend environment variables for the backend URL.
Configured CORS in FastAPI.
Tested communication between the React frontend and FastAPI backend.

landing Page 
Added the Helios name and tagline.
Added a simple explanation of what Helios does.
Added the Observe → Detect → Investigate → Explain → Recover flow.
Added interactive elements and animations.
Added a CTA leading to the login page.

what actually Codespace does 
Created a Codespace for the Helios repository.
Set up the Python environment.
Installed the required dependencies.
Added environment variables for MongoDB, Groq and Gemini.
Verified that Python and Docker work inside Codespaces.
- Move Monitoring Stack
Started Prometheus and cAdvisor inside Codespaces.
Forwarded the Prometheus port.
Confirmed that both Prometheus targets are UP.
- Move Test Containers
Started the three test containers:
server-1-cpu
server-2-mem
server-3-idle
Confirmed that the containers are running inside Codespaces.
- Move Backend
Started FastAPI using Uvicorn on port 8000.
Forwarded port 8000.
Confirmed that the Swagger UI can be opened from the browser.
- End-to-End Cloud Testing
Register the three test servers using Swagger UI.
Wait for CPU and memory incidents to be detected.
Check the incidents using /incidents.
Trigger recovery for one incident.
Confirm that the incident is resolved.
Complete the entire process from the browser without using the local machine for the test load.


<notes>
Mongo DB connected 
server health check 
metrics (Promotheus)
cd advisor 
(Running in Docker)
<i> Note:- Prometheus = a metrics collector + historian. Every 10 seconds (per our config), it goes and asks.

cAdvisor (and your FastAPI app) "what are your numbers right now?", timestamps the answer, and stores it. Over hours/days this builds up a real history you can query and graph — "show me CPU usage for the last hour," "was there a spike at 3pm yesterday." </i>

Detect Engine connected 

cpu spikes through stress test via docker 

Testing if the backend is following the lifecycle 

through docker run ,,, started the stress test 
 <i> Note :- 1) Metrics are of incident happened
 2)APScheduler --> reads Prometheus metrics
 3)Grok API and for Fallback Gemini(root cause, gives summary, )
 4)
 </i>
 daemonset.apps/cadvisor created — cAdvisor is now set to run as a DaemonSet: one copy on every node in your cluster (right now just 1 node, so 1 cAdvisor pod), collecting container metrics.
service/cadvisor created — a stable internal address (cadvisor:8080) other pods (like Prometheus) can use to reach it, without needing to know its actual pod IP (which can change).
configmap/prometheus-config created — your prometheus.yml config is now stored inside the cluster itself as a ConfigMap, so Prometheus can mount and read it like a regular file.
deployment.apps/prometheus created — Prometheus itself is now running as a managed pod; if it crashes, the Deployment automatically restarts it.
service/prometheus created — same idea as cAdvisor's service: a stable address (prometheus:9090) inside the cluster to reach Prometheus.
 

