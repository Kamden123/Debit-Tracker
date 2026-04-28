# Debit Tracker

Debit Tracker is a Flask web application for tracking consumptive-use water reserve debits. I designed and developed Debit Tracker for Okanogan County's planning workflow, allowing staff a faster way to enter debit records, apply reserve-specific rules, search records, and generate reserve-capacity reports. Debit Tracker eliminated the need to use an exterior vendor for the same service.

This portfolio version uses SQLite sample data so it can be reviewed and run locally without access to the original internal database.

## Why I Built It

The original workflow involved sending county data off to an exterior vendor. I built this application to reduce manual tracking, improve consistency, make reporting easier for staff, and cut out the exterior vendor which reduced update time and planning operation cost.

## Features

- Add, edit, delete, and search debit records
- Search by parcel number, reserve, or basin
- Dynamic reserve debit rule dropdowns
- Auto-filled debit quantity based on selected reserve/rule
- Auto-filled basin based on selected reserve
- SQLite demo database seeded with sample records
- Multi-page PDF capacity report generation
- Clean Flask route structure and reusable report module

## Tech Stack

- Python
- Flask
- SQLite for the demo version
- HTML templates
- Matplotlib
- NumPy

## Database Configuration

This demo version uses SQLite for ease of setup and portability.

In production, this application was originally designed to work with PostgreSQL and real operational data systems. The SQLite version allows the application to run locally without requiring external database configuration.

To adapt this back to PostgreSQL, the database connection layer can be easily modified.

## Screens to Demo
1. Debit Records page - shows searchable records and action buttons.
2. Add Debit page - shows the custom form workflow.
3. Reserve dropdown - changing the reserve updates available debit rules.
4. Reserve Debit Rule dropdown - changing the rule updates the quantity automatically.
5. PDF Report - generates a consumptive-use offset report from grouped records.

## How to Run Locally

### 1. Clone the repository


git clone https://github.com/Kamden123/Debit-Tracker.git
cd Debit-Tracker


### 2. Create and activate a virtual environment

Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1


macOS/Linux:

python3 -m venv .venv
source .venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Run the application

python app.py

Open your browser to:
http://127.0.0.1:5000

The application will create a local SQLite database file named `debit_tracker_demo.sqlite3` on first run and seed it with sample records.

## How to Generate the PDF Report

Click "Download PDF Report" in the navigation bar, or visit:

http://127.0.0.1:5000/report

The generated report is based on grouped debit totals by reserve. The portfolio version writes the report to the "reports/" folder and returns it as a browser download.

## Project Structure

├── app.py                  # Flask routes, database setup, CRUD logic
├── report.py               # PDF report generation logic
├── requirements.txt        # Python dependencies
├── templates/
│   ├── base.html           # Shared layout
│   ├── index.html          # Records list/search page
│   └── form.html           # Add/edit form workflow
├── static/
│   └── favicon.ico
├── reports/                # Generated reports are written here
└── README.md

## Notes on the Original Version

The original internal version connected to PostgreSQL and supported production county workflow data. This public portfolio version intentionally removes production credentials, internal network addresses, and private data. It uses local sample records to demonstrate the application design and functionality safely.

## Project Skills

This project demonstrates practical software development for internal operations workflow:

- Translating a business process into a working web application
- Designing form-based workflows
- Integrating application logic with structured data
- Creating reporting tools for non-technical users
- Writing maintainable Python modules
