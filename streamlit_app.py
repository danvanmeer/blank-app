import streamlit as st
import pandas as pd
from io import StringIO
import requests
import json
import os

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    st.write(stringio)

    # To read file as string:
    string_data = stringio.read()
    st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)



# -----------------------
# Configuration
# -----------------------
TOKEN = (
    "Bearer eyJhbGciOiJFZERTQSIsImtpZCI6ImE1NDI4NzlhLTJkZDQtNjgyMi04NDMyLTg2Zjk1OTQzZTY3NiJ9."
    "eyJhdWQiOiJzaGlwaGVybyIsImV4cCI6MTc2NzQwNjk2NSwiaWF0IjoxNzM1ODUwMDEzLCJpc3MiOiJodHRwczov"
    "L29wcy5jb3Jlc2lnbmFsLmNvbTo4MzAwL3YxL2lkZW50aXR5L29pZGMiLCJuYW1lc3BhY2UiOiJyb290IiwicHJl"
    "ZmVycmVkX3VzZXJuYW1lIjoic2hpcGhlcm8iLCJzdWIiOiJmYTBjNGM5Yy1jMjFjLWZmZGYtYzBiOS00OGFlZDVh"
    "ZjljMTYiLCJ1c2VyaW5mbyI6eyJzY29wZXMiOiJjZGFwaSJ9fQ."
    "m4O8buKNc4Ofw1K5Kqlr_1msde5RJ_-LvvfNqlbgGb1wVSmKDBMQ5q3ExZQsdfyg0v0KUfHQl1ZVBzT578tdDA"
)

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': TOKEN
}

SEARCH_URL = "https://api.coresignal.com/cdapi/v1/professional_network/job/search/filter"
COLLECT_URL = "https://api.coresignal.com/cdapi/v1/professional_network/job/collect"

# -----------------------
# Helper Functions
# -----------------------

def get_company_name_from_domain(domain: str) -> str:
    """
    Extract the company name from the domain by taking everything
    before the first '.' in the domain.
    E.g., 'mielleorganics.com' -> 'mielleorganics'
    """
    return domain.split('.')[0] if '.' in domain else domain

def fetch_job_posting_ids(domain: str, keyword_description: str = "'information technology' OR 'IT' OR 'warehouse'") -> list:
    """
    Use the first snippet to retrieve a list of job posting IDs for the given domain.
    """
    payload = {
        "company_domain": domain,
        "keyword_description": keyword_description
    }

    response = requests.post(
        SEARCH_URL,
        headers=HEADERS,
        data=json.dumps(payload)
    )

    if response.status_code != 200:
        print(f"[ERROR] Failed to retrieve job postings for {domain}: {response.text}")
        return []

    # The API response in your snippet suggests it's simply a JSON array of IDs.
    # Adjust parsing here if the actual structure is different.
    try:
        job_ids = response.json()  # e.g. [231918683, 244701157, 249905497, ...]
        # Make sure we have a list
        if isinstance(job_ids, list):
            return job_ids
        else:
            print(f"[WARNING] Unexpected JSON structure for domain '{domain}': {job_ids}")
            return []
    except json.JSONDecodeError:
        print(f"[ERROR] Unable to parse JSON for domain '{domain}': {response.text}")
        return []

def fetch_job_details(job_id: int) -> dict:
    """
    Use the second snippet to retrieve details for a single job posting ID.
    """
    job_url = f"{COLLECT_URL}/{job_id}"
    response = requests.get(job_url, headers=HEADERS)

    if response.status_code != 200:
        print(f"[WARNING] Failed to retrieve job details for ID={job_id}: {response.text}")
        return {}

    try:
        # Return the job details as a dictionary
        return response.json()
    except json.JSONDecodeError:
        print(f"[ERROR] Unable to parse JSON for job ID={job_id}: {response.text}")
        return {}

# -----------------------
# Main Execution
# -----------------------

def analyze_files():
    # 1. Read domains from domains.txt
    #    Each line in 'domains.txt' should contain one domain (e.g. "mielleorganics.com")
    #if not os.path.exists("domains.txt"):
    #    print("[ERROR] 'domains.txt' not found. Please create it and list one domain per line.")
    #    return

    with stringio as f:
        domains = [line.strip() for line in f if line.strip()]
    
    print(f"File uploaded")

    # 2. For each domain, retrieve job IDs
    for domain in domains:
        print(f"Processing domain: {domain}")
        company_name = get_company_name_from_domain(domain)

        job_ids = fetch_job_posting_ids(domain=domain)

        # If no job IDs found, skip
        if not job_ids:
            print(f"No job IDs found for {domain}. Skipping file creation.")
            continue

        # 2a. Write job IDs to "COMPANY NAME - job posting IDs.txt"
        job_ids_filename = f"{company_name} - job posting IDs.txt"
        with open(job_ids_filename, "w") as f_out:
            for jid in job_ids:
                f_out.write(str(jid) + "\n")
        print(f"Saved job posting IDs to '{job_ids_filename}'")

        # 3. For each job ID, retrieve details and combine into a single JSON array
        job_details_list = []
        for jid in job_ids:
            details = fetch_job_details(jid)
            if details:
                job_details_list.append(details)

        # Write the combined JSON to "COMPANY NAME - job details.json"
        job_details_filename = f"{company_name} - job details.json"
        with open(job_details_filename, "w", encoding="utf-8") as json_out:
            json.dump(job_details_list, json_out, indent=4)
        print(f"Saved job details to '{job_details_filename}'")

#if __name__ == "__main__":
#   main()

st.button("Run Analysis", use_container_width=True, on_click=analyze_files)