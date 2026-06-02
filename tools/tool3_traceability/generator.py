import os
import json
import anthropic
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


def generate_test_cases(req_id: str, req_name: str, description: str,
                         rationale: str, verification_method: str) -> list[dict]:
    """
    Calls Claude API to generate test cases for a single requirement.
    Returns list of dicts with keys matching TRACEABILITY_CSV_FIELDS.
    """
    prompt = f"""You are a systems engineering verification expert.

Generate test cases for the requirement below. Follow these rules:
- Each test case must fully verify a distinct aspect of the requirement
- Use test types: HIL (Hardware-in-the-Loop), FAT (Factory Acceptance Testing), SAT (Site Acceptance Testing)
  - HIL: simulation-based tests with real software and simulated hardware signals
  - FAT: tests run at the manufacturer facility before delivery
  - SAT: tests run at the customer site after delivery
- Verification method must be one of: Test, Analysis, Inspection, Demonstration
- Pass/Fail Criteria must be a specific, measurable condition (no vague language)
- Generate between 2 and 4 test cases per requirement
- Test IDs use format: TEST-[SUBSYSTEM]-[NNN] (derive subsystem from the requirement ID: {req_id})

Return ONLY a valid JSON array with no markdown, no explanation:
[
  {{
    "test_id": "TEST-[SUBSYSTEM]-001",
    "test_name": "Short name (5-10 words)",
    "description": "Step-by-step test procedure (2-4 sentences)",
    "requirement_id": "{req_id}",
    "verification_method": "Test | Analysis | Inspection | Demonstration",
    "test_type": "HIL | FAT | SAT",
    "pass_fail_criteria": "Specific measurable pass condition",
    "status": "Draft"
  }}
]

Requirement ID: {req_id}
Requirement Name: {req_name}
Description: {description}
Rationale: {rationale}
Verification Method (from requirement): {verification_method}
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
    if isinstance(parsed, dict):
        parsed = [parsed]
    if not isinstance(parsed, list):
        raise ValueError(f"Unexpected response format from API: {type(parsed)}")
    return parsed
