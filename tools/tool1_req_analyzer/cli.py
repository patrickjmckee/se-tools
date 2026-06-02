import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
from . import analyzer, rewriter, formatter
from .config import CONFIDENCE_THRESHOLD

# Load .env from the project root (se-tools/.env) if present
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _prompt_clarifications(questions: list[str]) -> str:
    if not questions:
        return ""

    print()
    collected = []
    for q in questions:
        print(f"  Q: {q}")
        print("     (press Enter to skip / type 'none' if no details available)")
        answer = input("  A: ").strip()
        if answer.lower() in ("", "none", "n/a", "no", "skip"):
            continue
        collected.append(f"Q: {q}\nA: {answer}")

    return "\n\n".join(collected)


def _run_single(text: str, output_csv: str) -> None:
    result = analyzer.analyze(text)
    formatter.print_analysis(result)

    if result.issues and not result.meets_threshold:
        print(
            f"\nConfidence ({result.confidence:.0%}) is below threshold "
            f"({CONFIDENCE_THRESHOLD:.0%}). Clarification needed before rewrite."
        )
        formatter.print_questions(result.clarifying_questions)
        supplemental = _prompt_clarifications(result.clarifying_questions)
        result.supplemental_info = supplemental

        # Re-score: if user provided any info, bump confidence enough to attempt rewrite
        if supplemental.strip():
            result.confidence = max(result.confidence + 0.20, CONFIDENCE_THRESHOLD)
            print(f"\nConfidence updated to: {result.confidence:.0%} (user input applied)")
        else:
            print("\nNo additional details provided.")

    if result.meets_threshold:
        print("\nGenerating rewrite via Claude API...")
        try:
            data = rewriter.rewrite(result)
            formatter.print_rewrite(data)
            formatter.append_to_csv(data, output_csv)
        except Exception as e:
            print(f"\nRewrite failed: {e}", file=sys.stderr)
    else:
        print(
            f"\nConfidence ({result.confidence:.0%}) still below threshold. "
            "Rewrite skipped. Resolve flagged issues and re-run."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="req-analyzer",
        description="Requirements Quality Analyzer -- flags issues and rewrites requirements.",
    )
    parser.add_argument(
        "--text", "-t",
        help="Requirement text to analyze (quoted string).",
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to a text file with one requirement per line.",
    )
    parser.add_argument(
        "--output", "-o",
        default="requirements_output.csv",
        help="Output CSV file path (default: requirements_output.csv).",
    )
    args = parser.parse_args()

    if not args.text and not args.file:
        # Interactive mode
        print("Requirements Quality Analyzer")
        print("Enter requirement text (or 'quit' to exit).\n")

    def run_loop(text: str) -> None:
        _run_single(text, args.output)
        print()
        again = input("Analyze another requirement? (y/n): ").strip().lower()
        if again in ("y", "yes"):
            next_text = input("\nEnter requirement text: ").strip()
            if next_text.lower() not in ("quit", "exit", "q"):
                run_loop(next_text)

    if args.text:
        _run_single(args.text, args.output)
        print()
        again = input("Analyze another requirement? (y/n): ").strip().lower()
        if again in ("y", "yes"):
            next_text = input("\nEnter requirement text: ").strip()
            if next_text:
                run_loop(next_text)

    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        for line in lines:
            _run_single(line, args.output)
            print()
        print(f"Batch complete. {len(lines)} requirement(s) processed.")

    else:
        first = input("Enter requirement text: ").strip()
        if first.lower() not in ("quit", "exit", "q"):
            run_loop(first)
