
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
REGISTRY_FILE = BASE_DIR / "company_boards.json"

SUPPORTED_SOURCES = [
    "greenhouse",
    "lever",
    "ashby"
]


def load_company_boards():

    if not REGISTRY_FILE.exists():
        raise FileNotFoundError(
            "company_boards.json file not found."
        )

    with REGISTRY_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Invalid company registry format.")

    for source in SUPPORTED_SOURCES:

        if source not in data:
            data[source] = []

        if not isinstance(data[source], list):
            raise ValueError(
                f"{source} must contain a list."
            )

    return data


def validate_registry():

    data = load_company_boards()

    valid_entries = []
    errors = []
    seen = set()

    for source in SUPPORTED_SOURCES:

        for index, entry in enumerate(data[source], start=1):

            if not isinstance(entry, dict):
                errors.append(
                    f"{source}: Entry {index} must be an object."
                )
                continue

            company = entry.get("company")
            board = entry.get("board")

            if not isinstance(company, str) or not company.strip():
                errors.append(
                    f"{source}: Company name missing at entry {index}."
                )
                continue

            if not isinstance(board, str) or not board.strip():
                errors.append(
                    f"{source}: Board ID missing at entry {index}."
                )
                continue

            company = company.strip()
            board = board.strip()

            key = (source, board.lower())

            if key in seen:
                errors.append(
                    f"{source}: Duplicate board ID {board}."
                )
                continue

            seen.add(key)

            valid_entries.append({
                "source": source,
                "company": company,
                "board": board
            })

    return valid_entries, errors


def get_all_company_boards():

    entries, errors = validate_registry()

    if errors:
        raise ValueError("\n".join(errors))

    return entries


if __name__ == "__main__":

    entries, errors = validate_registry()

    print("\nCareerIntel Company Registry")
    print("----------------------------")

    for source in SUPPORTED_SOURCES:

        count = sum(
            1 for entry in entries
            if entry["source"] == source
        )

        print(f"{source.title()}: {count} companies")

    print("----------------------------")
    print("Total companies:", len(entries))

    if errors:
        for error in errors:
            print("ERROR:", error)
    else:
        print("Registry structure is valid.")
