import argparse
import csv
import sys
from pathlib import Path
from dotenv import load_dotenv
from . import generator, formatter

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

REQUIRED_INPUT_FIELDS = {"ID", "Name", "Description", "Rationale", "Verification Method"}


def _read_requirements(input_path: str) -> list[dict]:
    path = Path(input_path)
    if not path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("Error: input CSV is empty.", file=sys.stderr)
        sys.exit(1)

    missing = REQUIRED_INPUT_FIELDS - set(rows[0].keys())
    if missing:
        print(f"Error: input CSV missing fields: {', '.join(sorted(missing))}", file=sys.stderr)
        sys.exit(1)

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="traceability",
        description="Test Traceability Matrix Generator -- generates test cases from requirements CSV.",
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to requirements CSV (output from Tool 1).",
    )
    parser.add_argument(
        "--output", "-o",
        default="traceability_matrix.csv",
        help="Output CSV file path (default: traceability_matrix.csv).",
    )
    args = parser.parse_args()

    rows = _read_requirements(args.input)
    total = len(rows)
    print(f"Loaded {total} requirement(s) from {args.input}")
    print(f"Output: {args.output}\n")

    all_test_count = 0
    for i, row in enumerate(rows, 1):
        req_id = row["ID"]
        req_name = row["Name"]
        description = row["Description"]
        rationale = row.get("Rationale", "")
        verification_method = row.get("Verification Method", "Test")

        print(f"[{i}/{total}] Generating test cases for {req_id}...")
        try:
            test_cases = generator.generate_test_cases(
                req_id, req_name, description, rationale, verification_method
            )
            formatter.print_test_cases(req_id, test_cases)
            formatter.append_to_csv(test_cases, args.output)
            all_test_count += len(test_cases)
        except Exception as e:
            print(f"  Failed for {req_id}: {e}", file=sys.stderr)

    print(f"\nDone. {all_test_count} test case(s) written to {args.output}")
