Agentic Data Quality Copilot


A fully automated data quality pipeline that fetches, transforms, and audits data daily — then uses an AI agent to read the ETL logs, reason about what went wrong, and fire an email alert before anyone has to check manually.











Why I Built This

Data quality issues in pipelines are usually caught late — either by a downstream analyst who notices something wrong in a dashboard, or by a customer who hits a bug caused by bad data. By that point the damage is done.

Most teams handle this with hand-written SQL checks or basic row-count validations. They work until they don't — and they require someone to actively look at the results.

I wanted to build something closer to how a data engineer actually thinks about a failed pipeline: read the logs, understand what the data should look like, identify what's off, and explain it in plain English to whoever's on call. That's what the AI agent does here. The rest of the pipeline (Airflow + PySpark + Bronze layer) gives it something real to audit.

What It Does

Every day the pipeline runs automatically and:


Pulls products, users, and orders from an API into raw JSON

Transforms and normalizes the raw data into a clean Bronze layer using PySpark

Passes the ETL logs to a GPT-4o-mini agent that reads them and reasons about data quality

Sends an email alert with a plain-English summary if anything looks wrong


No manual checking. No dashboards to refresh. If there's a problem, it shows up in your inbox.


Screenshots


Add a screenshot of the Airflow DAG graph view and a sample agent summary output here — visuals make a big difference for anyone evaluating the project.




Tech Stack

Layer	Technology	Purpose	
Orchestration	Apache Airflow	DAG scheduling, task dependencies, retry logic	
ETL Engine	PySpark	Distributed data transformation	
Data Storage	Raw + Bronze (medallion)	Structured ingestion layers	
AI Agent	OpenAI GPT-4o-mini	Log analysis and data quality reasoning	
Containerization	Docker Compose	Reproducible local environment	
Language	Python 3.11+	Pipeline logic, agent runner	
Alerting	SMTP Email	Automated issue notification	



Architecture

                    ┌─────────────────────┐
                    │   Apache Airflow     │
                    │   (DAG Scheduler)    │
                    └────────┬────────────┘
                             │ triggers in order
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        api_fetcher     spark_etl      agent_runner
              │              │              │
              ▼              ▼              ▼
       /data/raw/     /data/bronze/   reads ETL logs
       products.json  products/       + bronze stats
       users.json     users/               │
       orders.json    orders/              ▼
                           │         GPT-4o-mini
                    writes ETL log    reasons about
                           │         quality issues
                           └──────────────┤
                                          ▼
                                   agent_summary.txt
                                   ISSUES_FOUND=True/False
                                          │
                                  ┌───────┴───────┐
                                  │  Issues found? │
                                  │  Yes → Email   │
                                  │  No  → Done    │
                                  └───────────────┘


Design Decisions

Why Airflow for orchestration?
The pipeline has four distinct steps with real dependencies — Spark can't run until the raw data exists; the agent can't run until Spark has written its logs. Airflow's DAG model handles this naturally and gives you retry logic, task-level logging, and a UI to see exactly where a run failed. A cron script would work until one step fails silently.

Why PySpark for a pipeline this size?
Honestly, pandas would handle this data volume fine. The reason I used PySpark is that the Bronze layer pattern — raw → cleaned → standardized — is the same pattern used in production data lake architectures at scale. Using PySpark here means the same ETL code could run on a 100GB dataset with minimal changes. It's about building the habit and the pattern, not the volume.

Why Bronze layer specifically?
The medallion architecture (Bronze → Silver → Gold) is industry standard for data lake design. Bronze means "landed exactly as it arrived, just cleaned up enough to be usable" — no business logic applied yet. Keeping raw and bronze separate means you can always re-derive downstream layers from the source without re-fetching from the API.

Why GPT-4o-mini for the agent?
The reasoning task here — read logs, identify anomalies, write a summary — doesn't require a large model. GPT-4o-mini is fast and cheap enough to run daily without meaningful cost. The agent prompt tells it what a healthy pipeline looks like so it has a baseline to compare against.


Prerequisites


Docker Desktop (v24+) — everything runs in containers

OpenAI API key — for the AI agent step

SMTP credentials — for email alerts (Gmail app password works)



Quick Start

1. Clone the repo

git clone https://github.com/BalajiV21/Agentic_dataQuality-copilot.git
cd Agentic_dataQuality-copilot


2. Configure environment

Create airflow/.env:

# OpenAI
OPENAI_API_KEY=your_openai_key_here

# Email alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_RECIPIENT=team@yourcompany.com



For Gmail, use an App Password (not your account password). Generate one at myaccount.google.com → Security → App Passwords.



3. Start the stack

docker compose up -d


This starts Airflow (webserver + scheduler), the Spark environment, and all dependencies.

4. Access Airflow

http://localhost:8080

username: airflow
password: airflow


5. Trigger the pipeline

In the Airflow UI, find the dq_pipeline DAG and click the play button. You'll see four tasks run in sequence:

api_fetch → spark_etl → agent_runner → email_alert



Pipeline Steps

Step 1 — API Fetch (Raw Layer)

Pulls products, users, and orders from a public API and lands them as raw JSON:

/opt/airflow/data/raw/products.json
/opt/airflow/data/raw/users.json
/opt/airflow/data/raw/orders.json


Step 2 — PySpark ETL (Bronze Layer)

Reads the raw JSON, normalizes nested fields, filters out unusable rows, and writes partitioned Parquet to the Bronze layer:

/opt/airflow/data/bronze/products/
/opt/airflow/data/bronze/users/
/opt/airflow/data/bronze/orders/


ETL stats (row counts, null rates, schema) are written to a log file for the agent to read.

Step 3 — AI Agent (Data Quality Reasoning)

The agent reads the ETL log and checks for:


Missing or null values above threshold

Row counts that are unexpectedly low or high

Fields with invalid formats (negative quantities, malformed emails, etc.)


It generates a plain-English summary and stamps the result:

Products seem complete.
Users list has 2 records missing email.
Orders contain invalid quantity values.

ISSUES_FOUND=True


Output saved to /opt/airflow/data/agent_summary.txt.

Step 4 — Email Alert

If ISSUES_FOUND=True, an email goes out automatically:

Subject: Data Quality Issue Detected

Hi Team,
The pipeline detected data quality issues today.

- 2 user records missing email field
- 1 product has a negative stock value

ISSUES_FOUND=True


If everything looks clean, no email is sent.


Project Structure

agentic-data-quality-copilot/
├── airflow/
│   ├── dags/
│   │   ├── dq_pipeline_dag.py     # Main DAG definition
│   │   └── utils/
│   │       ├── api_fetcher.py     # Raw data ingestion
│   │       ├── spark_etl.py       # PySpark transformation
│   │       └── agent_runner.py    # OpenAI agent + email logic
│   ├── Dockerfile
│   ├── .env                       # Your credentials (not committed)
│   └── requirements.txt
├── docker-compose.yml
└── README.md



Challenges &amp; What I Learned

Getting PySpark to run inside the Airflow Docker container
This was the most time-consuming part of the setup. Airflow's official Docker image doesn't include Java or Spark. I had to build a custom Dockerfile that extends the Airflow base image, installs the right JDK version, and configures JAVA_HOME correctly. Small version mismatches between PySpark and Java caused silent failures that took a while to track down.

Prompt engineering for the agent
The first version of the agent prompt was too open-ended — it would return inconsistently formatted summaries and sometimes skip the ISSUES_FOUND tag entirely, which broke the email step. I had to be explicit in the prompt about the exact output format and give it clear definitions of what counts as an "issue". Getting an LLM to reliably produce structured output without a schema enforcer took more iteration than I expected.

Task dependency ordering in Airflow
Airflow's DAG definition can be tricky when tasks share state through files on disk rather than XComs. If the Spark task writes its log to a path and the agent task reads from that same path, there's no guarantee the file is fully flushed before the next task starts unless you explicitly model the dependency. I learned to always check task completion signals rather than assuming file availability.

Email delivery in a local Docker environment
SMTP from inside a Docker container has firewall and port forwarding quirks depending on the host OS. On Windows in particular, port 587 needs explicit configuration. I ended up testing with a dedicated Gmail App Password and documenting the exact setup steps after hitting several "connection refused" errors.


What's Next


Silver layer — add a transformation step that applies business rules and deduplication on top of Bronze

Slack alerts — alongside email, push a summary to a Slack channel using a webhook

Great Expectations integration — replace the custom null-check logic with a proper data validation framework

Metrics dashboard — store agent summaries over time and visualize quality trends in a simple Streamlit UI



License

MIT


Built by Balaji Viswanathan
