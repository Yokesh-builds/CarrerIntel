# CareerIntel – Multi-Source Job Discovery Platform

## 1. Project Overview

CareerIntel is a multi-source job discovery platform developed to collect job opportunities from different company recruitment platforms and display them in one centralised application.

The system integrates three public job-posting APIs:

- Greenhouse
- Lever
- Ashby

Each recruitment platform provides job information in a different JSON format. CareerIntel collects the available job postings, extracts important information, converts the data into a common structure, removes duplicate records and stores the results in a central SQLite database.

Users can search and filter the collected job opportunities through a web interface.

The main objective is to simplify job discovery by bringing job postings from multiple company career pages into one searchable platform.

## 2. Project Objectives

- Integrate Greenhouse, Lever and Ashby public job APIs.
- Collect published job opportunities from configured company boards.
- Extract important job information from API responses.
- Standardise job records into a common data structure.
- Identify and remove duplicate records.
- Store collected job information in a central database.
- Provide keyword-based job search.
- Support filtering by company, location and job source.
- Display job details and original application links.
- Expand company coverage through a verified company-board registry.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Backend web application |
| Requests | External API communication |
| SQLAlchemy | Database ORM |
| SQLite | Central job database |
| HTML | Website structure |
| CSS | Website styling |
| JavaScript | Frontend interactions |
| JSON | Company board configuration and structured data |
| python-dotenv | Environment configuration |

## 4. System Architecture and Workflow

CareerIntel follows a structured data collection and processing workflow.

Greenhouse API + Lever API + Ashby API

↓

Collect job postings

↓

Extract and standardise job information

↓

Remove duplicate records

↓

Store in central database

↓

Search, filter and display jobs

### Step 1: API Integration

The application connects to three public recruitment APIs.

**Greenhouse Job Board API**

Endpoint:

`https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true`

It retrieves published job information from a configured Greenhouse company board.

**Lever Postings API**

Endpoint:

`https://api.lever.co/v0/postings/{site}?mode=json`

It retrieves published job postings from a configured Lever company site.

**Ashby Public Job Postings API**

Endpoint:

`https://api.ashbyhq.com/posting-api/job-board/{board_name}?includeCompensation=true`

It retrieves published job information from a configured Ashby job board.

The application uses Python Requests to send HTTP GET requests and receives JSON responses.

Each company must have a valid board identifier.

### Step 2: Job Data Collection

The collectors module contains separate functions for each recruitment platform:

- `collect_greenhouse(board)`
- `collect_lever(board)`
- `collect_ashby(board)`

Each function sends a request to its respective API and extracts the available job postings.

The system collects available information such as:

- Job ID
- Job title
- Company
- Location
- Department
- Employment type
- Published date
- Job description
- Original job URL

The availability of individual fields depends on the information published by each employer.

### Step 3: Data Extraction and Standardisation

Greenhouse, Lever and Ashby use different field names and response structures.

For example:

| Information | Greenhouse | Lever | Ashby |
|---|---|---|---|
| Job title | title | text | title |
| Job ID | id | id | id |
| Location | location.name | categories.location | location |
| Description | content | descriptionPlain | descriptionPlain |
| Job URL | absolute_url | hostedUrl | jobUrl |

CareerIntel uses a common normalisation function called `normalize_job()`.

It converts the different API responses into one standard job structure.

Example:

```json
{
  "source": "Greenhouse",
  "external_id": "12345",
  "title": "Python Developer",
  "company": "Example Company",
  "location": "Chennai",
  "department": "Engineering",
  "employment_type": "Full-time",
  "posted_at": "2026-11-20",
  "job_url": "https://example.com/job",
  "description": "Python developer required..."
}
```

This common structure makes it easier to store, search and manage jobs from different sources.

The description cleaning function also extracts readable text from HTML job descriptions.

### Step 4: Duplicate Detection

The same job opportunity may be collected more than once during the collection process.

CareerIntel uses duplicate detection to avoid storing repeated records as separate unique jobs.

The current source-level duplicate identification uses:

- Source name
- External job ID

These fields are combined to identify an existing record from the same recruitment platform.

The database also uses a unique constraint on source and external job ID to prevent duplicate source records.

This method detects repeated records from the same source. It does not guarantee detection of similar job postings published by different companies or different ATS platforms.

### Step 5: Central Database Storage

CareerIntel uses SQLite as its central database for the current proof of concept.

SQLAlchemy manages database models and database operations.

The job table stores information such as:

- Internal job ID
- Source
- External job ID
- Job title
- Company
- Location
- Department
- Employment type
- Published date
- Job URL
- Job description

The collection process supports inserting new records and updating existing records.

This keeps the database organised and avoids repeated insertion of the same source-level job.

### Step 6: Search, Filtering and Display

After job collection and database storage, users can access the collected opportunities through the CareerIntel website.

The application supports:

- Keyword-based job search
- Multiple comma-separated search keywords
- Company filtering
- Location filtering
- Job source filtering
- Latest-first sorting
- Pagination
- Individual job details
- Original job application links

Users can search for opportunities without visiting multiple company career pages separately.

## 5. Company Board Registry

CareerIntel uses a company-board registry to manage the companies from which jobs are collected.

The `company_boards.json` file stores company information for the three supported recruitment sources.

Example:

```json
{
  "greenhouse": [
    {
      "company": "Example Company",
      "board": "example-company"
    }
  ],
  "lever": [],
  "ashby": []
}
```

The board identifier is required to access the corresponding company's public job postings.

The `board_registry.py` module loads and validates the configured company entries.

The `validate_boards.py` module checks whether configured board identifiers are accessible through the respective API endpoints.

The project aims to expand coverage to more than 100 verified companies.

This is a target, not an automatic global company discovery feature. Companies must be identified and their board identifiers verified before collection.

## 6. Initial Job Indexing

Initial indexing is the first bulk collection and preparation of available job postings from the configured company boards.

The process includes:

1. Configure company board identifiers.
2. Request published jobs from the three APIs.
3. Extract the available job information.
4. Convert the records into a common structure.
5. Remove repeated source-level records.
6. Insert job records into SQLite.
7. Prepare the stored information for search and retrieval.

During subsequent collection runs, the application can identify existing records and update them instead of inserting duplicates.

The current project uses structured database storage and column indexes for selected fields.

Full-text indexing of job descriptions using SQLite FTS5 is a possible future enhancement and should not be considered implemented unless separately configured.

## 7. API Restrictions and Limitations

CareerIntel uses public job-posting endpoints. These APIs do not provide unrestricted access to every company's recruitment data.

Important limitations include:

**Company Board Identifiers**

Each company requires a valid Greenhouse board token, Lever site identifier or Ashby job-board name.

**Public Job Availability**

Only publicly exposed job postings can be collected.

**Missing Information**

Some job postings may not contain salary, employment type, department or other optional fields.

**API Rate Limits**

Excessive requests may be throttled or temporarily restricted. The application should use sensible request pacing and bounded retries.

**Company Coverage**

The APIs do not provide a complete global directory of companies using these platforms. CareerIntel must maintain a verified company-board registry.

**Other Recruitment Platforms**

Companies using Workday, LinkedIn, Indeed, SmartRecruiters and other platforms are outside the current three-source integration.

**Job Expiration**

Employers may close or remove job postings. Repeated synchronisation and job-status tracking are future improvements.

API access, data-use permissions and provider terms must be reviewed before production deployment.

## 8. Project Folder Structure

```text
CareerIntel_Poc/
│
├── app.py
├── main.py
├── collectors.py
├── database.py
├── board_registry.py
├── validate_boards.py
├── company_boards.json
├── .env
├── careerintel.db
├── requirements.txt
│
├── templates/
│   ├── index.html
│   └── job_details.html
│
├── static/
│   └── style.css
│
├── data/
├── output/
├── outputs/
│
└── venv/
```

## 9. Installation and Setup

### Prerequisites

- Python 3.10 or later
- Visual Studio Code or another Python editor
- Internet connection
- Git (optional)

### Step 1: Open the project folder

```powershell
cd "CareerIntel_Poc"
```

### Step 2: Create a virtual environment

```powershell
python -m venv venv
```

### Step 3: Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 5: Configure company boards

Add verified company board identifiers to:

`company_boards.json`

### Step 6: Validate the company registry

```powershell
python board_registry.py
```

### Step 7: Validate API board identifiers

```powershell
python validate_boards.py
```

### Step 8: Run the job collection application

```powershell
python main.py
```

Select the collection option from the terminal menu.

### Step 9: Start the website

```powershell
python app.py
```

Open the application in your browser:

`http://127.0.0.1:5000`

## 10. Terminal Collection Options

The command-line application provides three options:

1. Collect and store jobs.
2. Search jobs.
3. Exit.

After collection, the terminal displays a summary containing:

- Total collected jobs
- Unique jobs
- Duplicate records removed
- New jobs inserted
- Existing jobs updated
- Source errors

The actual collection count depends on the configured company boards and the job postings available at the time of the request.

## 11. Expected Outcomes

- Integration with Greenhouse, Lever and Ashby public job APIs.
- Collection of published job opportunities from configured companies.
- A common structure for job information.
- Reduced repeated source-level job records.
- Centralised SQLite storage.
- Keyword-based job search and filtering.
- A web interface for job discovery.
- A scalable company-board configuration approach.

## 12. Future Enhancements

- Expand the company registry to 100+ verified companies.
- Add scheduled job collection.
- Implement retry handling and collection monitoring.
- Add better job expiration and status tracking.
- Implement SQLite FTS5 or PostgreSQL full-text search.
- Evaluate PostgreSQL for larger production workloads.
- Add salary and skills extraction when data is available.
- Explore vector search and semantic job discovery.
- Improve near-duplicate detection across different sources.
- Add CSV export and collection reports.

## 13. Conclusion

CareerIntel provides a centralised approach to job discovery by integrating multiple public recruitment platforms.

The application follows a structured data workflow involving API integration, job collection, data extraction, standardisation, duplicate detection, database storage and search.

By maintaining a common job data structure, CareerIntel makes it easier to manage and discover job opportunities from different company career platforms.

The project can be expanded with more verified company boards, improved indexing methods and additional search capabilities in future development.

## 14. Official API Documentation

- Greenhouse Job Board API: https://developers.greenhouse.io/job-board.html
- Lever Postings API: https://github.com/Lever/postings-api
- Ashby Public Job Postings API: https://developers.ashbyhq.com/docs/public-job-posting-api
- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- SQLite Documentation: https://www.sqlite.org/docs.html
