
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAXONOMY = ROOT / "09_CONFIG" / "taxonomy"
OUTPUT = ROOT / "08_LOGS" / "taxonomy_semantic_review.txt"

FILES = [
    ("activities.json", "activities"),
    ("subdomains.json", "subdomains"),
]


def load_records(filename, expected_key):
    path = TAXONOMY / filename

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    records = data.get(expected_key, [])

    if not isinstance(records, list):
        raise ValueError(
            f"{filename}: expected '{expected_key}' to be a list."
        )

    return records


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    total = 0

    with OUTPUT.open("w", encoding="utf-8") as report:
        report.write("CV-AI TAXONOMY SEMANTIC REVIEW\n")
        report.write("=" * 72 + "\n\n")

        for filename, key in FILES:
            records = load_records(filename, key)
            pending = [
                item for item in records
                if item.get("review_status") == "GENERATED_NEEDS_REVIEW"
            ]

            total += len(pending)

            report.write(f"\nFILE: {filename}\n")
            report.write("-" * 72 + "\n")
            report.write(f"Pending records: {len(pending)}\n\n")

            for number, item in enumerate(pending, start=1):
                report.write(f"[{number}] ")
                report.write(str(item.get("id", "(missing ID)")))
                report.write("\n")

                # Print all fields except bulky nested structures.
                for field, value in item.items():
                    if field == "id":
                        continue

                    rendered = json.dumps(
                        value,
                        ensure_ascii=False,
                        indent=2
                    )

                    report.write(f"  {field}:\n")

                    for line in rendered.splitlines():
                        report.write(f"    {line}\n")

                report.write("\n")

        report.write("\n" + "=" * 72 + "\n")
        report.write(f"TOTAL PENDING RECORDS: {total}\n")

    print("Review report generated.")
    print(f"Records awaiting review: {total}")
    print(f"Report: {OUTPUT}")


if __name__ == "__main__":
    main()
