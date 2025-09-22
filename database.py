import sqlite3
import json

DB_NAME = "reports.db"

def init_db():
    """Initializes the database and creates the 'reports' table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            report_content TEXT NOT NULL,
            sources TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_report(query, report_content, sources):
    """Adds a new report to the database, returns the new report's ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Store the list of sources as a JSON string
    sources_json = json.dumps(sources)
    cursor.execute(
        "INSERT INTO reports (query, report_content, sources) VALUES (?, ?, ?)",
        (query, report_content, sources_json)
    )
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id

def get_all_reports():
    """Retrieves all reports for the history page."""
    conn = sqlite3.connect(DB_NAME)
    # Use Row factory to access columns by name
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, query, created_at FROM reports ORDER BY created_at DESC")
    reports = cursor.fetchall()
    conn.close()
    return reports

def get_report_by_id(report_id):
    """Retrieves a single, complete report by its ID."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    report = cursor.fetchone()
    if report:
        # Convert the row object to a dictionary and decode the sources JSON
        report_dict = dict(report)
        report_dict['sources'] = json.loads(report_dict['sources'])
        return report_dict
    return None