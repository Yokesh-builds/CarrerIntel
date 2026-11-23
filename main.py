
from board_registry import get_all_company_boards

from collectors import (
    collect_greenhouse,
    collect_lever,
    collect_ashby
)

from database import (
    initialize_database,
    save_jobs,
    search_jobs
)


# Supported job collection sources
COLLECTORS = {
    "greenhouse": collect_greenhouse,
    "lever": collect_lever,
    "ashby": collect_ashby
}


def remove_duplicates(jobs):

    unique_jobs = []
    seen = set()

    for job in jobs:

        key = (
            job["source"].lower(),
            job["external_id"]
        )

        if key in seen:
            continue

        seen.add(key)
        unique_jobs.append(job)

    duplicates = len(jobs) - len(unique_jobs)

    return unique_jobs, duplicates


def collect_all_jobs():

    all_jobs = []
    errors = []

    try:
        companies = get_all_company_boards()

    except Exception as error:
        print(f"Registry error: {error}")
        return all_jobs, [str(error)]

    if not companies:
        print("No company boards configured in company_boards.json.")
        return all_jobs, errors

    print(f"\nTotal configured companies: {len(companies)}")

    for entry in companies:

        source = entry["source"].lower()
        company = entry["company"]
        board = entry["board"]

        collector = COLLECTORS.get(source)

        if collector is None:
            message = f"Unsupported source: {source}"
            errors.append(message)
            print(message)
            continue

        try:

            print(
                f"\nCollecting {source.title()} jobs "
                f"from {company} ({board})..."
            )

            jobs = collector(board)

            # Use the company display name in the results
            for job in jobs:
                if (
                    not job.get("company")
                    or job["company"].strip().lower() == board.lower()
                ):
                    job["company"] = company

            all_jobs.extend(jobs)

            print(
                f"Collected {len(jobs)} jobs from {company}."
            )

        except Exception as error:

            message = f"{source.title()} / {company}: {error}"

            errors.append(message)

            print(f"Collection error: {message}")

    return all_jobs, errors


def run_collection():

    initialize_database()

    collected, errors = collect_all_jobs()

    unique_jobs, duplicates = remove_duplicates(collected)

    inserted, updated = save_jobs(unique_jobs)

    print("\nCollection Summary")
    print("-------------------------")
    print("Collected jobs:", len(collected))
    print("Unique jobs:", len(unique_jobs))
    print("Duplicates removed:", duplicates)
    print("New jobs inserted:", inserted)
    print("Existing jobs updated:", updated)
    print("Source errors:", len(errors))

    for error in errors:
        print("-", error)


def run_search():

    keyword = input(
        "Enter job title, company, location: "
    ).strip()

    jobs, total = search_jobs(
        keyword=keyword,
        page=1,
        per_page=50
    )

    print(f"\nFound {total} matching jobs.\n")

    for job in jobs:

        print("Title:", job.title)
        print("Company:", job.company)
        print("Location:", job.location)
        print("Source:", job.source)
        print("Apply:", job.job_url)
        print("-" * 50)


def main():

    initialize_database()

    while True:

        print("\nCareerIntel Job Discovery")
        print("-------------------------")
        print("1. Collect and store jobs")
        print("2. Search jobs")
        print("3. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":

            run_collection()

        elif choice == "2":

            run_search()

        elif choice == "3":

            print("Exiting CareerIntel.")
            break

        else:

            print("Invalid option. Please try again.")


if __name__ == "__main__":
     main()
