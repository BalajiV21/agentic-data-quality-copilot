
#  **Agentic Data Quality Copilot — End-to-End Airflow + PySpark + Agentic AI Pipeline**

### **Modern Data Engineering Pipeline with Airflow • PySpark • Delta Bronze Layer • Agentic AI Alerts (via OpenAI)**


---

##  **Project Overview**

This project is a fully automated **Agentic Data Quality Pipeline** that fetches data from APIs, performs ETL using **PySpark**, analyzes the pipeline quality using **Agentic AI**, and sends automatic alerts using Airflow.

The pipeline combines:

* **Airflow** (Orchestration)
* **PySpark** (ETL + data processing)
* **Agentic AI (OpenAI GPT-4o-mini)** (Data quality reasoning)
* **Docker** (Containerization)
* **Bronze Data Lake** (Raw → Bronze layer)

The project runs end-to-end every day and generates:

 Raw data
 Cleaned Bronze layer
 ETL logs
 Agent Data Quality summary
 Email alerts if issues found

---


##  **Project Structure**

```
agentic-data-quality-copilot/
│
├── airflow/
│   ├── dags/
│   │   ├── dq_pipeline_dag.py
│   │   └── utils/
│   │       ├── api_fetcher.py
│   │       ├── spark_etl.py
│   │       └── agent_runner.py
│   ├── Dockerfile
│   ├── .env
│   └── requirements.txt
│
├── docker-compose.yml
└── README.md
```

---

#  **Pipeline Steps**

## 1️ API Fetcher (Raw Layer)

* Pulls products, users, and orders from a public dummy API
* Saves into:

```
/opt/airflow/data/raw/products.json
/opt/airflow/data/raw/users.json
/opt/airflow/data/raw/orders.json
```

---

## 2️ PySpark ETL (Bronze Layer)

* Reads the raw data
* Normalizes nested JSON
* Selects required fields
* Writes Bronze layer:

```
/opt/airflow/data/bronze/products/
opt/airflow/data/bronze/users/
opt/airflow/data/bronze/orders/
```

---

## 3️ Agentic AI (Data Quality Reasoning)

The AI:

* Reads ETL logs
* Detects missing values
* Detects abnormal counts
* Generates human-friendly summary
* Add final tag:

```
ISSUES_FOUND=True or False
```

Output saved to:

```
/opt/airflow/data/agent_summary.txt
```

---

## 4️ Airflow Email Alerts

If the AI finds issues → email is sent.

---

#  **Run the Entire Project Using Docker**

### **Start Services**

```
docker compose up -d
```

### **Access Airflow**

```
http://localhost:8080
```

**username:** airflow
**password:** airflow

---

# **Trigger the DAG**

In Airflow UI → Trigger “dq_pipeline”

This runs:

1. API Fetch
2. Spark ETL
3. Agentic AI
4. Email

---

#  **Agent Summary Example**

Example output:

```
Products seem complete.
Users list has 2 records missing email.
Orders contain invalid quantity values.

ISSUES_FOUND=True
```

---

#  **Automatic Email Example**

```
Subject: Data Quality Issue Detected

Hi Team,
The pipeline detected data quality issues today.

- 2 user records missing email
- 1 product has negative stock

ISSUES_FOUND=True
```

---

#  **Tech Used**

| Component     | Technology             |
| ------------- | ---------------------- |
| Orchestration | Airflow (Docker)       |
| ETL Engine    | Apache Spark / PySpark |
| Data Layer    | Raw + Bronze           |
| AI            | OpenAI GPT-4o-mini     |
| Orchestration | Airflow DAG            |
| Environment   | Docker Compose         |
| Language      | Python 3               |

---

#  **End-to-End Pipeline Output**

After a successful run, you will see:

- Raw files
- Bronze data
- ETL logs
- AI summary
- Email alerts (if needed)







