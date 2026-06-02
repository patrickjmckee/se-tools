VAGUE_ADJECTIVES = [
    "bad", "good", "safe", "unsafe", "adequate", "inadequate", "sufficient",
    "insufficient", "fast", "slow", "quick", "reliable", "unreliable", "robust",
    "appropriate", "acceptable", "reasonable", "proper", "effective", "efficient",
    "optimal", "satisfactory", "suitable", "correct", "incorrect", "accurate",
    "inaccurate", "stable", "unstable", "secure", "insecure", "minimal", "maximal",
    "necessary", "unnecessary", "simple", "complex", "easy", "difficult",
    "instantly", "immediately", "always", "never", "real-time", "realtime",
]

# Vague terms that appear as words/phrases (checked separately from word-boundary match)
VAGUE_PHRASES = [
    "real-time", "real time", "in real-time", "in real time",
    "health info", "health information", "status info", "system info",
]

WEAK_MODALS = ["should", "may", "might", "could", "would"]

RELATIVE_TERMS = [
    "reduce", "increase", "improve", "enhance", "minimize", "maximize",
    "decrease", "faster", "slower", "higher", "lower", "better", "worse",
    "more", "less", "greater", "fewer", "larger", "smaller",
]

UNDEFINED_CONDITIONS = [
    "when needed", "if required", "if conditions allow", "as necessary",
    "when appropriate", "if applicable", "when possible", "as needed",
    "under certain conditions", "in some cases", "where necessary",
    "if necessary", "when warranted", "something goes wrong", "goes wrong",
    "any issue", "any problem", "any fault", "in an emergency",
    "under emergency", "when necessary",
]

# Patterns that indicate a compound requirement (multiple shall-statements bundled)
COMPOUND_CONJUNCTIONS = [" and ", " as well as ", " in addition to ", " also "]

# Weight of each issue type toward confidence deduction (0.0-1.0 each)
ISSUE_WEIGHTS = {
    "vague_adjective":         0.20,
    "weak_modal":              0.15,
    "missing_quantification":  0.25,
    "undefined_condition":     0.20,
    "relative_term":           0.20,
    "ambiguous_subject":       0.15,
    "compound_requirement":    0.15,
    "unquantified_latency":    0.20,
    "unquantified_availability": 0.20,
}

CONFIDENCE_THRESHOLD = 0.80

JAMA_CSV_FIELDS = [
    "ID", "Name", "Description", "Rationale",
    "Verification Method", "Linked Standard", "Status",
]

VERIFICATION_METHODS = ["Test", "Analysis", "Inspection", "Demonstration"]

LINKED_STANDARDS = [
    "ISO 26262", "IEC 61508", "IEC 62061",
    "ISO/IEC 29148", "ISO 9001", "ISO 14971", "None",
]

MODEL = "claude-sonnet-4-6"
