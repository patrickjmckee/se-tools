import re
from dataclasses import dataclass, field
from typing import Optional
from .config import (
    VAGUE_ADJECTIVES, VAGUE_PHRASES, WEAK_MODALS, RELATIVE_TERMS,
    UNDEFINED_CONDITIONS, COMPOUND_CONJUNCTIONS, ISSUE_WEIGHTS, CONFIDENCE_THRESHOLD,
)


@dataclass
class Issue:
    code: str
    description: str
    token: Optional[str] = None


@dataclass
class AnalysisResult:
    raw_text: str
    issues: list[Issue] = field(default_factory=list)
    clarifying_questions: list[str] = field(default_factory=list)
    confidence: float = 1.0
    supplemental_info: str = ""

    @property
    def meets_threshold(self) -> bool:
        return self.confidence >= CONFIDENCE_THRESHOLD


def analyze(text: str) -> AnalysisResult:
    result = AnalysisResult(raw_text=text)
    lower = text.lower()
    words = re.findall(r"\b[\w-]+\b", lower)
    has_number = bool(re.search(r"\d+", text))

    # Vague adjectives (word-boundary match) -- collect unique tokens
    seen_vague_tokens: set[str] = set()
    found_vague = [w for w in VAGUE_ADJECTIVES if w in words]
    for w in found_vague:
        if w not in seen_vague_tokens:
            seen_vague_tokens.add(w)
            result.issues.append(Issue(
                code="VAGUE",
                description=f'"{w}" is undefined -- no measurable threshold.',
                token=w,
            ))

    # Vague phrases (substring match) -- skip if a sub-token already reported
    for phrase in VAGUE_PHRASES:
        if phrase in lower:
            # Suppress if every word in the phrase is already individually flagged
            phrase_words = set(phrase.replace("-", " ").split())
            if not phrase_words.issubset(seen_vague_tokens):
                canonical = phrase.replace("in ", "").strip()
                if canonical not in seen_vague_tokens:
                    seen_vague_tokens.add(canonical)
                    result.issues.append(Issue(
                        code="VAGUE",
                        description=f'"{phrase}" is undefined -- specify the data parameters and update rate.',
                        token=phrase,
                    ))

    # Weak modals
    found_modals = [w for w in WEAK_MODALS if w in words]
    for w in found_modals:
        result.issues.append(Issue(
            code="MODAL",
            description=f'"{w}" is ambiguous -- use "shall" for mandatory requirements.',
            token=w,
        ))

    # Relative terms without quantification
    found_relative = [w for w in RELATIVE_TERMS if w in words]
    for w in found_relative:
        result.issues.append(Issue(
            code="RELATIVE",
            description=f'"{w}" is relative -- no baseline or numeric target specified.',
            token=w,
        ))

    # Undefined conditions -- report only the longest matching phrase to avoid duplicates
    matched_conditions: list[str] = [p for p in UNDEFINED_CONDITIONS if p in lower]
    # Remove shorter phrases that are substrings of a longer match
    deduped_conditions: list[str] = []
    for phrase in sorted(matched_conditions, key=len, reverse=True):
        if not any(phrase in longer for longer in deduped_conditions):
            deduped_conditions.append(phrase)
    for phrase in deduped_conditions:
        result.issues.append(Issue(
            code="CONDITION",
            description=f'"{phrase}" is undefined -- specify the measurable trigger condition.',
            token=phrase,
        ))

    # Missing quantification: no number anywhere in the requirement
    if not has_number:
        result.issues.append(Issue(
            code="UNQUANTIFIED",
            description="No numeric threshold or measurable value found in requirement.",
        ))

    # Unquantified latency: latency/timing words without a numeric value
    latency_terms = ["real-time", "real time", "instant", "instantly", "immediately",
                     "fast", "quickly", "rapid", "low-latency", "low latency"]
    has_latency_term = any(t in lower for t in latency_terms)
    has_latency_number = bool(re.search(r"\d+\s*(ms|millisecond|second|sec|hz|fps)", lower, re.IGNORECASE))
    if has_latency_term and not has_latency_number:
        result.issues.append(Issue(
            code="LATENCY",
            description='Timing/latency term present but no numeric bound specified (e.g., <= 100 ms).',
        ))

    # Unquantified availability: "always", "100%", without uptime/availability metric
    availability_terms = ["always", "never", "continuous", "continuously", "at all times"]
    has_availability_term = any(t in lower for t in availability_terms)
    has_availability_number = bool(re.search(r"\d+\s*%|\d+\s*nine|\buptime\b|\bavailability\b", lower, re.IGNORECASE))
    if has_availability_term and not has_availability_number:
        result.issues.append(Issue(
            code="AVAILABILITY",
            description='"always" / continuous availability claimed but no uptime metric or SLA defined (e.g., >= 99.9%).',
        ))

    # Compound requirement: multiple verbs/actions bundled with conjunctions
    conjunction_count = sum(1 for c in COMPOUND_CONJUNCTIONS if c in lower)
    verb_phrases = re.findall(r"\b(shall|must|will|should|can|let|allow)\b", lower)
    action_count = len(re.findall(r"\b(show|display|alert|notify|allow|enable|let|prevent|log|record|transmit|send|receive|control|stop|start)\b", lower))
    if conjunction_count >= 2 or (conjunction_count >= 1 and action_count >= 3):
        result.issues.append(Issue(
            code="COMPOUND",
            description=(
                f"Requirement bundles {action_count} distinct actions -- "
                "split into separate atomic requirements, one shall per requirement."
            ),
        ))

    # Ambiguous subject
    ambiguous_subject_pattern = r"\bthe system\b|\bit\b|\bthey\b|\bthem\b"
    if re.search(ambiguous_subject_pattern, lower):
        result.issues.append(Issue(
            code="SUBJECT",
            description='Subject is ambiguous ("them", "they", "it", or "the system") -- identify the specific component.',
        ))

    result.confidence = _score(result.issues)
    result.clarifying_questions = _build_questions(result.issues, text)
    return result


def _score(issues: list[Issue]) -> float:
    code_to_weight_key = {
        "VAGUE":        "vague_adjective",
        "MODAL":        "weak_modal",
        "UNQUANTIFIED": "missing_quantification",
        "CONDITION":    "undefined_condition",
        "RELATIVE":     "relative_term",
        "SUBJECT":      "ambiguous_subject",
        "COMPOUND":     "compound_requirement",
        "LATENCY":      "unquantified_latency",
        "AVAILABILITY": "unquantified_availability",
    }
    deduction = 0.0
    seen_codes = set()
    for issue in issues:
        if issue.code not in seen_codes:
            weight = ISSUE_WEIGHTS.get(code_to_weight_key.get(issue.code, ""), 0.0)
            deduction += weight
            seen_codes.add(issue.code)
    return max(0.0, 1.0 - deduction)


def _build_questions(issues: list[Issue], text: str) -> list[str]:
    questions = []
    codes = {i.code for i in issues}

    if "LATENCY" in codes:
        questions.append(
            "What is the maximum allowable latency for display updates and control response? (e.g., <= 100 ms, <= 500 ms)"
        )
    if "AVAILABILITY" in codes:
        questions.append(
            "What is the required system availability or uptime? (e.g., 99.9% uptime, no more than 1 hr/year downtime)"
        )
    if "VAGUE" in codes or "UNQUANTIFIED" in codes:
        questions.append(
            "What is the measurable threshold or numeric value that defines acceptable performance?"
        )
    if "CONDITION" in codes:
        questions.append(
            "What sensor, data source, or system event defines the fault/alert trigger condition?"
        )
    if "RELATIVE" in codes:
        questions.append(
            "What is the baseline value or reference point for comparison?"
        )
    if "COMPOUND" in codes:
        questions.append(
            "Should each action (display, alert, manual override) be a separate requirement with its own verification method?"
        )
    if "SUBJECT" in codes:
        questions.append(
            "Which specific component or subsystem is the subject? (e.g., C2 Ground Station UI, Operator Console)"
        )
    if "VAGUE" in codes or "CONDITION" in codes:
        questions.append(
            "What is the operating environment and what sensors/data sources are available?"
        )

    return questions
