"""
NationStates AI Governance Simulator
------------------------------------
Run this locally.  Before running:
  1. Replace YOUR_NATION and YOUR_PASSWORD below.
  2. Keep your password private - do NOT upload or share this file.
  3. Set a clear User-Agent string so moderators can contact you if needed.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import os
import json
from dotenv import load_dotenv

BASE = "https://www.nationstates.net/cgi-bin/api.cgi"
load_dotenv()
USER_AGENT = os.getenv("USER_AGENT")

# --- CONFIG ---
NATION = os.getenv("NATION")
PASSWORD = os.getenv("PASSWORD")
SLEEP_BETWEEN_REQUESTS = int(os.getenv("SLEEP_BETWEEN_REQUESTS", 10))
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"  # Set to true for testing without submitting
# ---------------

def ns_request(params, headers=None, data=None):
    """Generic GET or POST wrapper with rate-limit friendliness."""
    headers = headers or {}
    headers["User-Agent"] = USER_AGENT
    r = requests.request(
        "POST" if data else "GET",
        BASE,
        params=params if not data else None,
        data=data,
        headers=headers,
    )
    if r.status_code != 200:
        print(f"[!] HTTP {r.status_code} – {r.text[:120]}")
    return r


def fetch_issues():
    """Return all open issues for the nation."""
    headers = {"X-Password": PASSWORD}
    params = {"nation": NATION, "q": "issues"}
    r = ns_request(params, headers=headers)
    return BeautifulSoup(r.text, "xml")


def choose_option(issue_xml):
    """Use Ollama LLM to choose the best option instead of random."""
    options = issue_xml.find_all("OPTION")
    if not options:
        return None, "none"
    
    # Parse issue details
    title_elem = issue_xml.find("TITLE")
    text_elem = issue_xml.find("TEXT")
    title = title_elem.text if title_elem else ""
    text = text_elem.text if text_elem else ""
    
    # Build prompt
    prompt = f"You are the leader of a nation in NationStates. An issue has arisen:\n\n{title}\n{text}\n\nOptions:\n"
    for i, opt in enumerate(options, 1):
        prompt += f"{i}. {opt.text}\n"
    prompt += "\n\nChoose the best option for your nation by responding with a JSON object containing the key 'option_number' with the chosen option number (1, 2, 3, etc.). Consider economic stability, civil rights, and political freedom."
    
    # Call Ollama API with structured output
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False,
            "format": {
                "type": "object",
                "properties": {
                    "option_number": {"type": "integer"}
                },
                "required": ["option_number"]
            },
            "options": {"temperature": 0}  # Deterministic choices
        }, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # Parse the JSON response
            try:
                parsed = json.loads(data["response"])
                num = parsed["option_number"]
                if 1 <= num <= len(options):
                    return options[num-1]["id"], "AI"
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
    except (requests.RequestException, ValueError, KeyError):
        pass
    
    # Fallback to random if LLM fails
    chosen = random.choice(options)
    return chosen["id"], "random"


def answer_issue(issue_id, option_id):
    """Submit an issue decision."""
    headers = {"X-Password": PASSWORD}
    data = {
        "nation": NATION,
        "c": "issue",
        "issue": issue_id,
        "option": option_id,
    }
    r = ns_request({}, headers=headers, data=data)
    print(f"→ Answered issue {issue_id} with option {option_id}")
    return r.text


def run_once():
    issues = fetch_issues()
    for issue in issues.find_all("ISSUE"):
        issue_id = issue["id"]
        title = issue.find("TITLE").text if issue.find("TITLE") else ""
        text = issue.find("TEXT").text if issue.find("TEXT") else ""
        options = issue.find_all("OPTION")
        option_id, method = choose_option(issue)
        if option_id is not None:
            # Find chosen option text
            chosen_option_text = next((opt.text for opt in options if opt["id"] == option_id), "")
            # Log to NDJSON
            choice_data = {
                "timestamp": time.time(),
                "issue_id": issue_id,
                "title": title,
                "text": text,
                "option_id": option_id,
                "chosen_option_text": chosen_option_text,
                "method": method
            }
            with open("choices.ndjson", "a") as f:
                f.write(json.dumps(choice_data) + "\n")
            
            if TEST_MODE:
                print(f"[TEST] Would answer issue {issue_id} with option {option_id} ({method})")
            else:
                result = answer_issue(issue_id, option_id)
                print(result)
                time.sleep(SLEEP_BETWEEN_REQUESTS)


if __name__ == "__main__":
    if TEST_MODE:
        print("Running in TEST MODE - will not submit answers.")
        print("Checking for new issues…")
        run_once()
        print("Test completed.")
    else:
        while True:
            print("Checking for new issues…")
            run_once()
            print("Sleeping before next check.")
            time.sleep(3600)  # check every hour