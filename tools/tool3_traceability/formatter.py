import csv
import sys
from pathlib import Path
from .config import TRACEABILITY_CSV_FIELDS

SEP = "=" * 60


def print_test_cases(req_id: str, test_cases: list[dict]) -> None:
    print(f"\n{SEP}")
    print(f"TEST CASES FOR {req_id}")
    print(SEP)
    for tc in test_cases:
        print(f"\n  Test ID:             {tc.get('test_id', '')}")
        print(f"  Test Name:           {tc.get('test_name', '')}")
        print(f"  Description:         {tc.get('description', '')}")
        print(f"  Requirement ID:      {tc.get('requirement_id', '')}")
        print(f"  Verification Method: {tc.get('verification_method', '')}")
        print(f"  Test Type:           {tc.get('test_type', '')}")
        print(f"  Pass/Fail Criteria:  {tc.get('pass_fail_criteria', '')}")
        print(f"  Status:              {tc.get('status', '')}")
    print(SEP)


def append_to_csv(test_cases: list[dict], output_path: str) -> None:
    path = Path(output_path)
    write_header = not path.exists() or path.stat().st_size == 0

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRACEABILITY_CSV_FIELDS)
        if write_header:
            writer.writeheader()
        for tc in test_cases:
            row = {
                "Test ID": tc.get("test_id", ""),
                "Test Name": tc.get("test_name", ""),
                "Description": tc.get("description", ""),
                "Requirement ID": tc.get("requirement_id", ""),
                "Verification Method": tc.get("verification_method", ""),
                "Test Type": tc.get("test_type", ""),
                "Pass/Fail Criteria": tc.get("pass_fail_criteria", ""),
                "Status": tc.get("status", "Draft"),
            }
            writer.writerow(row)
