import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

LOG_PATH = "/opt/airflow/data/etl_log.json"
SUMMARY_PATH = "/opt/airflow/data/agent_summary.txt"


def load_etl_log():
    """Load ETL log from file."""
    if not os.path.exists(LOG_PATH):
        return None
    with open(LOG_PATH, "r") as f:
        return json.load(f)


def run_agent():
    """Runs the AI agent to analyze ETL output."""
    log = load_etl_log()
    if log is None:
        print("No ETL log found. Agent cannot run.")
        return

    client = OpenAI()   # Uses OPENAI_API_KEY from environment (.env)

    prompt = f"""
You are a Data Quality Analyst AI system. You are given an ETL log with
record counts, status, and detected issues.

Here is the ETL log:
{json.dumps(log, indent=4)}

TASK:
- Summarize the ETL results in simple English.
- Explain any data quality issues.
- Add 'ISSUES_FOUND=True' if there are issues.
- Add 'ISSUES_FOUND=False' if everything is clean.

OUTPUT FORMAT:
1. Summary text
2. LAST LINE must be ONLY:

ISSUES_FOUND=True
or
ISSUES_FOUND=False
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",      # Cheapest good model
        messages=[
            {"role": "system", "content": "You are an AI data quality analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )

    summary_text = response.choices[0].message.content.strip()

    with open(SUMMARY_PATH, "w") as f:
        f.write(summary_text)

    print("Agent summary saved:", SUMMARY_PATH)


def main():
    print("Running Agentic AI...")
    run_agent()


if __name__ == "__main__":
    main()
