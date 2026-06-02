import os
import anthropic
from .analyzer import AnalysisResult
from .config import MODEL

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def rewrite(result: AnalysisResult) -> dict:
    """
    Calls Claude API to rewrite a flagged requirement.
    Returns dict with keys: id, name, description, rationale,
    verification_method, linked_standard, status.
    """
    issues_block = "\n".join(
        f"  [{i.code}] {i.description}" for i in result.issues
    )
    supplemental = (
        f"\nAdditional context provided by the engineer:\n{result.supplemental_info}"
        if result.supplemental_info.strip()
        else ""
    )

    prompt = f"""You are a systems engineering requirements expert following ISO/IEC 29148.

Rewrite the requirement below. Fix every flagged issue. Apply this pattern exactly:
  measurable trigger condition + "[Subject] shall [action] [quantified threshold]"

Return ONLY valid JSON with these exact keys (no markdown, no explanation):
{{
  "id": "REQ-[SUBSYSTEM]-001",
  "name": "Short descriptive name (5-10 words)",
  "description": "Full rewritten shall statement",
  "rationale": "One sentence explaining why this requirement exists",
  "verification_method": "Test | Analysis | Inspection | Demonstration",
  "linked_standard": "ISO 26262 | IEC 61508 | IEC 62061 | ISO/IEC 29148 | ISO 9001 | ISO 14971 | None",
  "status": "Draft"
}}

Original requirement:
{result.raw_text}

Issues detected:
{issues_block}
{supplemental}

Rules:
- Replace all vague adjectives with measurable values
- Use "shall" not "should", "may", or "must"
- Include numeric thresholds where feasible; use [SPECIFY: <what is needed>] as a placeholder where values are unknown
- Infer reasonable values for autonomous vehicle / robotics context when not specified
- Choose the most applicable linked standard
- Choose verification method based on whether the requirement is measurable (Test), model-provable (Analysis), visual (Inspection), or behavioral (Demonstration)
"""

    client = _get_client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:]).rstrip("`").strip()
    # Extract first JSON object if Claude wrapped output in an array
    parsed = json.loads(raw)
    if isinstance(parsed, list):
        parsed = parsed[0]
    if not isinstance(parsed, dict):
        raise ValueError(f"Unexpected response format from API: {type(parsed)}")
    return parsed
