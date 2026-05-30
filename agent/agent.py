from mistralai.client import Mistral
import subprocess
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

client_ai = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

SYSTEM_PROMPT = """You are Morning First Mate, a personal AI productivity 
assistant with a fun pirate personality. Your job is to help the user 
start their day with a clear, actionable morning briefing based on their 
real data from GitHub, Google Calendar, and Notion.

Always format your response with these exact sections:
Good Morning, Captain!
Today's Schedule
GitHub Activity
Notion Tasks
Your Mission Today (top 3 priorities)

Keep it concise, motivating, and pirate-themed but professional.
If a data source returns no data, say so briefly and move on."""

def run_coral_query(query):
    try:
        result = subprocess.run(
            ["coral", "sql", query],
            capture_output=True,
            text=True,
            timeout=30,
            shell=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            return "No data found"
    except Exception as e:
        return f"Query error: {str(e)}"

def get_morning_briefing():
    print("Fetching GitHub repos...")
    github_repos = run_coral_query(
        "SELECT full_name, description FROM github.user_repos LIMIT 5"
    )
    
    print("Fetching calendar...")
    calendar_today = run_coral_query(
        "SELECT summary, start_time, end_time FROM google_calendar.events WHERE date(start_time) = date('now') ORDER BY start_time LIMIT 10"
    )
    
    print("Fetching Notion pages...")
    notion_pages = run_coral_query(
        "SELECT * FROM notion.search LIMIT 5"
    )

    print("Fetching GitHub issues...")
    github_issues = run_coral_query(
        "SELECT full_name, open_issues_count FROM github.user_repos WHERE open_issues_count > 0 LIMIT 5"
    )
    
    print("Generating briefing with Gemini...")
    
    data_context = f"""
{SYSTEM_PROMPT}

Here is the user's real live data:

GITHUB REPOSITORIES:
{github_repos}

GITHUB REPOS WITH OPEN ISSUES:
{github_issues}

TODAY'S GOOGLE CALENDAR EVENTS:
{calendar_today}

NOTION PAGES:
{notion_pages}

IMPORTANT: You MUST generate ALL 5 sections in your response.
Even if some data is empty, generate content for every section.
For "Your Mission Today" - always give exactly 3 priorities based 
on the GitHub data even if calendar and notion are empty.
Format each section clearly starting with the section name.
Never say "No data found" for Your Mission Today - always 
generate priorities from whatever data is available.
"""
    
    response = client_ai.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": data_context}]
    )
    return response.choices[0].message.content

def chat(user_message, history=[]):
    context = f"{SYSTEM_PROMPT}\n\nUser: {user_message}"
    response = client_ai.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": context}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Morning First Mate - Fetching your data...\n")
    briefing = get_morning_briefing()
    print(briefing)
