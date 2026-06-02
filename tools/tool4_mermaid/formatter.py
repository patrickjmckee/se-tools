from pathlib import Path

SEP = "=" * 60


def print_diagram(result: dict) -> None:
    print(f"\n{SEP}")
    print(f"MERMAID DIAGRAM -- {result.get('type_label', '').upper()}")
    print(SEP)
    print(f"\nTitle: {result.get('title', '')}")
    print(f"Notes: {result.get('notes', '')}")
    print(f"\n```mermaid")
    print(result.get("mermaid", ""))
    print("```")
    print(SEP)


def save_to_file(result: dict, output_path: str) -> None:
    path = Path(output_path)
    title = result.get("title", "Diagram")
    type_label = result.get("type_label", "")
    notes = result.get("notes", "")
    mermaid = result.get("mermaid", "")

    content = f"# {title}\n\n"
    content += f"**Type:** {type_label}\n\n"
    if notes:
        content += f"**Notes:** {notes}\n\n"
    content += f"```mermaid\n{mermaid}\n```\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
