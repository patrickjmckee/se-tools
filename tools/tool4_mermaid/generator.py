import os
import json
import anthropic
from .config import MODEL, DIAGRAM_TYPES

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def generate(description: str, diagram_type: str) -> dict:
    """
    Calls Claude API to generate a Mermaid diagram from a natural language description.

    Returns dict with keys:
      - diagram_type: str  (e.g. "classDiagram")
      - type_label: str    (e.g. "Block Definition Diagram")
      - mermaid: str       (raw Mermaid code, no fences)
      - title: str         (short diagram title)
      - notes: str         (brief explanation of what was generated)
    """
    mermaid_type, type_label = DIAGRAM_TYPES[diagram_type]

    if diagram_type == "auto":
        type_instruction = (
            "Choose the most appropriate Mermaid diagram type for the description. "
            "Use classDiagram for structure/component relationships (SysML BDD proxy), "
            "sequenceDiagram for message flows between components over time, or "
            "stateDiagram-v2 for system behavioral states and transitions."
        )
    else:
        type_instruction = f"Generate a {mermaid_type} diagram."

    prompt = f"""You are a systems engineering MBSE expert generating Mermaid diagrams as SysML proxies for use in Confluence.

{type_instruction}

Context: This is for a command-and-control system for autonomous robotic vehicles at Autonomous Solutions, Inc (ASI).
Domain: robotics, autonomous vehicles, C2 ground station software, telemetry, navigation, safety systems.

Return ONLY valid JSON with no markdown, no explanation:
{{
  "diagram_type": "classDiagram | sequenceDiagram | stateDiagram-v2",
  "type_label": "Block Definition Diagram | Sequence Diagram | State Machine Diagram",
  "title": "Short descriptive title (5-8 words)",
  "mermaid": "Raw Mermaid diagram code only -- no code fences, no triple backticks",
  "notes": "1-2 sentences explaining what the diagram captures and any key design decisions"
}}

Rules for diagram content:
- classDiagram: model subsystems as classes; use composition (--*), aggregation (--o), association (-->), dependency (..) relationships; include key attributes and methods; align with SysML BDD conventions
- sequenceDiagram: use descriptive participant names; include activation bars (activate/deactivate); show alt/opt/loop blocks where relevant; include error/fault paths if applicable
- stateDiagram-v2: define all operational states; label every transition with trigger condition and guard; include initial and final states; show fault and recovery paths

Description:
{description}
"""

    client = _get_client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:]).rstrip("`").strip()

    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError(f"Unexpected response format from API: {type(parsed)}")
    return parsed
