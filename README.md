AI Research Agent
This project is an AI-powered agent designed to automate the research process. It takes a user query, finds relevant online sources, extracts their content, and generates a concise, structured report using a local Large Language Model (LLM). All generated reports are saved in a local SQLite database for future reference.

Features
Web Interface: A simple and clean web UI built with Flask to enter queries and view past reports.

Web Search: Utilizes the Tavily API to find relevant and up-to-date online sources.

Content Extraction: Capable of extracting clean text from both HTML web pages and PDF documents.

AI Summarization: Leverages a local LLM (deepseek-r1:1.5b via Ollama) to generate structured summaries with key points.

Persistent Memory: Stores all past queries and their resulting reports in an SQLite database.

Error Handling: Handles common issues like failed web searches or content extraction errors, providing clear feedback to the user.

Architecture
The agent follows a simple, sequential workflow:

Input: The user submits a query through the Flask web interface.

Search: The query is sent to the Tavily API, which returns a list of relevant URLs.

Extract: The agent iterates through each URL, fetching the content and extracting clean text using trafilatura for HTML and pypdf for PDFs. It gracefully skips any sources it cannot access.

Summarize: The combined text content is passed to a local LLM (e.g., DeepSeek Coder) with a specific prompt to generate a structured report.

Store: The final report, along with the query and source links, is saved as a new entry in the SQLite database.

Display: The user is redirected to the new report's page, and the report is added to the history list on the main page.

How to Run
Follow these steps to set up and run the project locally.

Prerequisites
Python 3.8+

Ollama installed and running with a model of your choice (e.g., ollama pull deepseek-coder).

A Tavily API Key.

Installation
Clone the repository:

git clone [https://github.com/karanshewale0/AI-Agent-Assignment.git](https://github.com/karanshewale0/AI-Agent-Assignment.git)
cd your-repo-name

Create a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt

Set up your environment variables:
Create a file named .env in the project root and add your Tavily API key:

TAVILY_API_KEY="your_tavily_api_key_here"

Ensure your local LLM is running:
Make sure the Ollama application is running. You can check the model name you have installed by running ollama list. Update the model name in app.py if it's different from deepseek-coder:latest.

Running the Application
Initialize the database and start the web server:

python app.py

Access the web interface:
Open your browser and navigate to http://127.0.0.1:5000.

Type your query and the report with a summary of your chosen topic will be created.
