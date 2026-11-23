
import requests

from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit


HEADERS = {
    "User-Agent": "CareerIntel-PoC/1.0"
}

TIMEOUT = 30


class DescriptionParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        text = data.strip()

        if text:
            self.parts.append(text)


def clean_description(description):

    if not description:
        return ""

    parser = DescriptionParser()

    try:
        parser.feed(description)
        return " ".join(parser.parts)

    except Exception:
        return description


def get_json(url):

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    return response.json()


def clean_url(url):

    if not url:
        return None

    parts = urlsplit(url.strip())

    if parts.scheme not in ("http", "https"):
        return None

    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path.rstrip("/"),
        parts.query,
        ""
    ))


def normalize_job(
    source,
    job_id,
    title,
    company,
    location,
    department,
    employment_type,
    posted_at,
    job_url,
    description=None
):

    if job_id is None:
        return None

    return {
        "source": source,
        "external_id": str(job_id),
        "title": title or "Not specified",
        "company": company or "Not specified",
        "location": location or "Not specified",
        "department": department,
        "employment_type": employment_type,
        "posted_at": posted_at,
        "job_url": clean_url(job_url),
        "description": clean_description(description)
    }


def collect_greenhouse(board):

    url = (
        f"https://boards-api.greenhouse.io/v1/"
        f"boards/{board}/jobs?content=true"
    )

    data = get_json(url)

    jobs = []

    for item in data.get("jobs", []):

        location = item.get("location") or {}

        departments = item.get("departments") or []

        department = ", ".join(
            d.get("name", "")
            for d in departments
            if d.get("name")
        ) or None

        job = normalize_job(
            source="Greenhouse",
            job_id=item.get("id"),
            title=item.get("title"),
            company=board,
            location=location.get("name"),
            department=department,
            employment_type=None,
            posted_at=(
                item.get("first_published")
                or item.get("updated_at")
            ),
            job_url=item.get("absolute_url"),
            description=item.get("content")
        )

        if job:
            jobs.append(job)

    return jobs


def collect_lever(board):

    url = (
        f"https://api.lever.co/v0/"
        f"postings/{board}?mode=json"
    )

    data = get_json(url)

    jobs = []

    for item in data:

        categories = item.get("categories") or {}

        created = item.get("createdAt")

        posted_at = None

        if created:

            posted_at = datetime.fromtimestamp(
                created / 1000,
                tz=timezone.utc
            ).isoformat()

        job = normalize_job(
            source="Lever",
            job_id=item.get("id"),
            title=item.get("text"),
            company=board,
            location=categories.get("location"),
            department=categories.get("department"),
            employment_type=categories.get("commitment"),
            posted_at=posted_at,
            job_url=item.get("hostedUrl"),
            description=item.get("descriptionPlain")
        )

        if job:
            jobs.append(job)

    return jobs


def collect_ashby(board):

    url = (
        f"https://api.ashbyhq.com/posting-api/"
        f"job-board/{board}?includeCompensation=true"
    )

    data = get_json(url)

    jobs = []

    for item in data.get("jobs", []):

        if item.get("isListed") is False:
            continue

        job = normalize_job(
            source="Ashby",
            job_id=item.get("id"),
            title=item.get("title"),
            company=board,
            location=item.get("location"),
            department=item.get("department"),
            employment_type=item.get("employmentType"),
            posted_at=item.get("publishedAt"),
            job_url=item.get("jobUrl"),
            description=item.get("descriptionPlain")
        )

        if job:
            jobs.append(job)

    return jobs
