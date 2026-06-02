import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
from . import generator, formatter
from .config import DIAGRAM_TYPES

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _run_single(description: str, diagram_type: str, output_path: str) -> None:
    print(f"\nGenerating {DIAGRAM_TYPES[diagram_type][1]}...")
    try:
        result = generator.generate(description, diagram_type)
        formatter.print_diagram(result)
        formatter.save_to_file(result, output_path)
        print(f"\nSaved to: {output_path}")
    except Exception as e:
        print(f"\nGeneration failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mermaid-gen",
        description="Mermaid SysML Diagram Generator -- natural language description -> Mermaid diagram.",
    )
    parser.add_argument(
        "--text", "-t",
        help="Description of the subsystem or interaction to diagram (quoted string).",
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to a text file containing the description.",
    )
    parser.add_argument(
        "--type",
        choices=list(DIAGRAM_TYPES.keys()),
        default="auto",
        help="Diagram type: bdd (classDiagram), seq (sequenceDiagram), state (stateDiagram-v2), auto (Claude infers). Default: auto.",
    )
    parser.add_argument(
        "--output", "-o",
        default="diagram_output.md",
        help="Output markdown file path (default: diagram_output.md).",
    )
    args = parser.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        description = path.read_text(encoding="utf-8").strip()
    elif args.text:
        description = args.text.strip()
    else:
        print("Mermaid SysML Diagram Generator")
        print("Enter a description of the subsystem or interaction to diagram.\n")
        description = input("Description: ").strip()
        if description.lower() in ("quit", "exit", "q", ""):
            sys.exit(0)

    if not description:
        print("Error: description is empty.", file=sys.stderr)
        sys.exit(1)

    _run_single(description, args.type, args.output)

    try:
        print()
        again = input("Generate another diagram? (y/n): ").strip().lower()
        if again in ("y", "yes"):
            next_desc = input("\nDescription: ").strip()
            if next_desc and next_desc.lower() not in ("quit", "exit", "q"):
                next_type = input("Type (bdd/seq/state/auto) [auto]: ").strip().lower() or "auto"
                if next_type not in DIAGRAM_TYPES:
                    next_type = "auto"
                next_output = input("Output file [diagram_output.md]: ").strip() or "diagram_output.md"
                _run_single(next_desc, next_type, next_output)
    except EOFError:
        pass
