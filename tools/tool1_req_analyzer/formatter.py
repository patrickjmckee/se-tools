import csv
import os
from datetime import date
from .analyzer import AnalysisResult
from .config import JAMA_CSV_FIELDS


def print_analysis(result: AnalysisResult) -> None:
    print("\n" + "=" * 60)
    print("REQUIREMENTS QUALITY ANALYSIS")
    print("=" * 60)
    print(f"\nInput: {result.raw_text}\n")

    if not result.issues:
        print("No issues detected.")
    else:
        print(f"Issues found ({len(result.issues)}):")
        for i, issue in enumerate(result.issues, 1):
            token = f' [{issue.token}]' if issue.token else ""
            print(f"  {i}. [{issue.code}]{token} {issue.description}")

    print(f"\nConfidence score: {result.confidence:.0%}")
    print("=" * 60)


def print_questions(questions: list[str]) -> None:
    print("\nClarifying questions:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")


def print_rewrite(data: dict) -> None:
    print("\n" + "=" * 60)
    print("REWRITTEN REQUIREMENT")
    print("=" * 60)
    print(f"\nID:                  {data['id']}")
    print(f"Name:                {data['name']}")
    print(f"Description:         {data['description']}")
    print(f"Rationale:           {data['rationale']}")
    print(f"Verification method: {data['verification_method']}")
    print(f"Linked standard:     {data['linked_standard']}")
    print(f"Status:              {data['status']}")
    print("=" * 60)


def append_to_csv(data: dict, output_path: str) -> None:
    file_exists = os.path.isfile(output_path)
    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=JAMA_CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "ID":                  data["id"],
            "Name":                data["name"],
            "Description":         data["description"],
            "Rationale":           data["rationale"],
            "Verification Method": data["verification_method"],
            "Linked Standard":     data["linked_standard"],
            "Status":              data["status"],
        })
    print(f"\nSaved to: {output_path}")
