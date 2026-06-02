MODEL = "claude-sonnet-4-6"

DIAGRAM_TYPES = {
    "bdd":   ("classDiagram",    "Block Definition Diagram (SysML BDD proxy)"),
    "seq":   ("sequenceDiagram", "Sequence Diagram"),
    "state": ("stateDiagram-v2", "State Machine Diagram"),
    "auto":  (None,              "Claude infers best diagram type"),
}
