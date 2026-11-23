
# CareerIntel – Job Discovery Platform

## Project Overview

CareerIntel is a job discovery application that collects job
openings from Greenhouse, Lever and Ashby public job-board APIs.

The application stores collected job information in an SQLite
database and provides a web interface for searching and filtering
job opportunities.

## Technologies

- Python
- Flask
- SQLAlchemy
- SQLite
- Requests
- HTML
- CSS

## Features

1. Collect jobs from multiple job-board platforms.
2. Store job listings in SQLite.
3. Prevent duplicate records.
4. Update existing job information.
5. Search using multiple comma-separated keywords.
6. Apply AND search logic across job fields.
7. Filter by company, location and source.
8. View full job descriptions.
9. Open external application links.
10. Paginate search results.

## Search Logic

For example:

Python, SQL, Flask

Every keyword must match the same job listing.

The keywords can appear in different searchable fields,
including title, company, location, department and description.

## Installation

Install dependencies:

    python -m pip install -r requirements.txt

Initialize the database:

    python -c "from database import initialize_database; initialize_database()"

## Collect Jobs

    python main.py

Choose option 1 to collect jobs.

## Run Website

    python app.py

Open:

    http://127.0.0.1:5000

## Database

The project uses SQLite.

Database file:

    careerintel.db

## Job Sources

- Greenhouse
- Lever
- Ashby
