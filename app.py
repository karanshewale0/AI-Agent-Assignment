import os
import io
import openai
import requests
from tavily import TavilyClient
from dotenv import load_dotenv
from trafilatura import extract
from pypdf import PdfReader
from flask import Flask, render_template, request, redirect, url_for, flash

import database as db

# --- CONFIGURATION ---
load_dotenv()
app = Flask(__name__)
# A secret key is required for flashing messages
app.secret_key = os.urandom(24)

# Initialize API clients
llm_client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
try:
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
except KeyError:
    raise ValueError("TAVILY_API_KEY not found in .env file")

# --- CORE AGENT FUNCTIONS ---

def search_the_web(query: str):
    """Searches the web and handles potential errors."""
    print(f"🔍 Searching for: {query}")
    try:
        results = tavily_client.search(query=query, max_results=3)
        return [{"url": obj["url"]} for obj in results.get("results", [])]
    except Exception as e:
        # **ERROR HANDLING**: Inform the user if the search fails 
        flash(f"Error during web search: {e}", "error")
        return []

# ... (The extract_content_from_url and summarize_text functions remain the same as before)
def extract_content_from_url(url: str):
    print(f"📄 Extracting content from: {url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "application/pdf" in content_type:
            with io.BytesIO(response.content) as f:
                reader = PdfReader(f)
                text = "".join(page.extract_text() for page in reader.pages)
        elif "text/html" in content_type:
            text = extract(response.text)
        else:
            return None
        return text.strip() if text else None
    except requests.RequestException as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def summarize_text(query: str, content: str):
    print("🧠 Summarizing content...")
    if not content:
        return "Error: No content available to summarize."
    prompt = f"""Based on the following content, create a structured report about the query: "{query}". The report should include: 1. **Key Points**: A bulleted list of the most important findings. 2. **Summary**: A concise summary of the overall information. Here is the content:\n---\n{content}\n---"""
    try:
        response = llm_client.chat.completions.create(
            model="deepseek-r1:1.5b",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        # **ERROR HANDLING**: Inform the user if the LLM fails 
        flash(f"Error during summarization with LLM: {e}", "error")
        return None

# --- FLASK WEB ROUTES ---

@app.route("/")
def index():
    """Renders the home page with a list of past reports from the database."""
    reports = db.get_all_reports()
    return render_template("index.html", reports=reports)

@app.route("/generate", methods=["POST"])
def generate_report():
    query = request.form.get("query")
    if not query:
        flash("Please enter a query.", "error")
        return redirect(url_for("index"))

    sources = search_the_web(query)
    if not sources: # Error is flashed inside the search function
        return redirect(url_for("index"))

    all_content = ""
    successful_sources = []
    for source in sources:
        content = extract_content_from_url(source["url"])
        if content:
            all_content += content + "\n\n"
            successful_sources.append(source)
    
    if not all_content:
        # **ERROR HANDLING**: Inform user if no content could be extracted 
        flash("Failed to extract content from any of the found sources. Please try another query.", "error")
        return redirect(url_for("index"))

    report_content = summarize_text(query, all_content)
    if not report_content: # Error is flashed inside the summarize function
        return redirect(url_for("index"))

    # Save to database and redirect to the new report's page
    report_id = db.add_report(query, report_content, successful_sources)
    return redirect(url_for("view_report", report_id=report_id))

@app.route("/report/<int:report_id>")
def view_report(report_id):
    """Displays a specific report by fetching it from the database by its ID."""
    report = db.get_report_by_id(report_id)
    if not report:
        flash("Report not found.", "error")
        return redirect(url_for("index"))
    return render_template("report.html", report=report)

if __name__ == "__main__":
    db.init_db()  # Initialize the database on startup
    app.run(port=5000,debug=True)