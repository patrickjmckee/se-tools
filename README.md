# SE Tools

Systems engineering productivity tools for ASI. Built with Python 3.12 and the Anthropic Claude API.

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/patrickjmckee/se-tools.git
cd se-tools
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install the package

```bash
pip install -e .
```

For development tools (black, ruff, mypy, pytest):

```bash
pip install -e ".[dev]"
```

### 3. Set API key

Create `se-tools/.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

The `.env` file is gitignored. Do not commit it.

### 4. Run tools

After installation, tools are available as commands (venv must be active):

```bash
req-analyzer --text "..."
traceability --input requirements_output.csv
mermaid-gen --text "..."
```

Or run as Python modules from the project root:

```bash
python -m tools.tool1_req_analyzer
python -m tools.tool3_traceability --input requirements_output.csv
python -m tools.tool4_mermaid
```

---

## Tool 1 -- Requirements Quality Analyzer

Analyzes raw requirement text for quality issues. Flags violations of ISO/IEC 29148 and SE best practices. Generates a rewritten, Jama-importable requirement via Claude API when confidence >= 80%.

### Issue codes detected

| Code | Description |
|---|---|
| VAGUE | Undefined adjective with no measurable threshold (e.g., "safe", "fast", "real-time") |
| MODAL | Weak modal verb -- use "shall" not "should", "may", "might", "could", "would" |
| CONDITION | Undefined trigger condition (e.g., "something goes wrong", "when needed") |
| RELATIVE | Relative term with no baseline (e.g., "reduce", "improve", "increase") |
| UNQUANTIFIED | No numeric value or measurable threshold anywhere in the requirement |
| LATENCY | Timing/latency term present but no numeric bound (e.g., "quickly", "instantly") |
| AVAILABILITY | "Always" or continuous availability claimed but no uptime metric defined |
| COMPOUND | Multiple actions bundled in one requirement -- should be split into atomic requirements |
| SUBJECT | Ambiguous subject ("them", "they", "it", "the system") -- name the specific component |

### Confidence scoring

Each issue code deducts from a 100% confidence score:

| Code | Deduction |
|---|---|
| UNQUANTIFIED | 25% |
| VAGUE | 20% |
| CONDITION | 20% |
| RELATIVE | 20% |
| LATENCY | 20% |
| AVAILABILITY | 20% |
| COMPOUND | 15% |
| MODAL | 15% |
| SUBJECT | 15% |

- Confidence >= 80%: rewrite is generated automatically.
- Confidence < 80%: clarifying questions are presented before rewrite.
- If no additional details are provided after clarifying questions: rewrite is skipped.

### Usage

**Interactive mode (recommended):**

```bash
python3 -m tools.tool1_req_analyzer
```

Prompts for requirement text, runs analysis, asks clarifying questions if needed, generates rewrite, saves to CSV, then asks if another requirement should be analyzed.

**Single requirement via CLI flag:**

```bash
python3 -m tools.tool1_req_analyzer --text "The system should respond quickly when something goes wrong."
```

**Batch mode (one requirement per line in a text file):**

```bash
python3 -m tools.tool1_req_analyzer --file requirements_draft.txt
```

**Specify output CSV path:**

```bash
python3 -m tools.tool1_req_analyzer --text "..." --output /path/to/output.csv
```

Default output path: `requirements_output.csv` in the current working directory.

### Interactive session flow

```
Enter requirement text: The system should respond quickly when something goes wrong.

============================================================
REQUIREMENTS QUALITY ANALYSIS
============================================================

Issues found (4):
  1. [MODAL] [should] "should" is ambiguous -- use "shall"
  2. [CONDITION] [something goes wrong] undefined trigger condition
  3. [UNQUANTIFIED] No numeric threshold found
  4. [LATENCY] Timing term present but no numeric bound (e.g., <= 100 ms)

Confidence score: 20%
============================================================

Confidence (20%) is below threshold (80%). Clarification needed before rewrite.

Clarifying questions:
  1. What is the maximum allowable latency? (e.g., <= 100 ms, <= 500 ms)
  2. What is the measurable threshold for acceptable performance?
  3. What sensor or event defines the fault trigger condition?
  4. What is the operating environment?

  Q: What is the maximum allowable latency? (e.g., <= 100 ms, <= 500 ms)
     (press Enter to skip / type 'none' if no details available)
  A: <=500ms from fault detection to alert displayed on console

  [... remaining questions ...]

Confidence updated to: 80% (user input applied)

Generating rewrite via Claude API...

============================================================
REWRITTEN REQUIREMENT
============================================================

ID:                  REQ-CCS-001
Name:                Fault Detection to Operator Alert Latency Requirement
Description:         When any sensor reading exceeds defined operating limits or a
                     communication link loss is detected for greater than 2 seconds,
                     the command and control system shall display a fault alert
                     notification on the operator console within 500 milliseconds
                     of fault detection.
Rationale:           Timely operator notification is critical to enabling rapid
                     intervention and preventing unsafe robot behavior.
Verification method: Test
Linked standard:     ISO 26262
Status:              Draft
============================================================

Saved to: requirements_output.csv

Analyze another requirement? (y/n):
```

### Jama CSV import

Output CSV fields match Jama bulk import format:

| Field | Description |
|---|---|
| ID | REQ-[SUBSYSTEM]-[NNN] |
| Name | Short descriptive name |
| Description | Full "shall" statement |
| Rationale | One-sentence justification |
| Verification Method | Test / Analysis / Inspection / Demonstration |
| Linked Standard | ISO 26262 / IEC 61508 / IEC 62061 / ISO/IEC 29148 / ISO 9001 / ISO 14971 |
| Status | Draft / Review / Approved / Verified |

Jama supports import via: CSV (.csv), Excel (.xls, .xlsx), Word (.doc, .docx), ReqIF (.reqif, .reqifz).

---

## Tool 3 -- Test Traceability Matrix Generator

Reads a requirements CSV (output from Tool 1) and generates test cases for each requirement via Claude API. Produces a traceability matrix CSV linking each test to its parent requirement.

### Output CSV fields

| Field | Description |
|---|---|
| Test ID | TEST-[SUBSYSTEM]-[NNN] |
| Test Name | Short descriptive name |
| Description | Step-by-step test procedure |
| Requirement ID | Linked REQ-[SUBSYSTEM]-[NNN] |
| Verification Method | Test / Analysis / Inspection / Demonstration |
| Test Type | HIL / FAT / SAT |
| Pass/Fail Criteria | Measurable pass condition |
| Status | Draft |

### Test types

| Type | Description |
|---|---|
| HIL | Hardware-in-the-Loop -- simulated hardware signals with real software, run at ASI |
| FAT | Factory Acceptance Testing -- at ASI facility before delivery |
| SAT | Site Acceptance Testing -- at customer site after delivery |

### Usage

```bash
python3 -m tools.tool3_traceability --input requirements_output.csv
```

**Specify output path:**

```bash
python3 -m tools.tool3_traceability --input requirements_output.csv --output traceability_matrix.csv
```

Default output path: `traceability_matrix.csv` in the current working directory.

Generates 2-4 test cases per requirement. Prints each test case to console as it is generated, then writes all results to the output CSV.

---

## Tool 4 -- Mermaid SysML Diagram Generator

Takes a natural language description of a subsystem or interaction and generates a Mermaid diagram via Claude API. Diagrams render natively in Confluence and serve as lightweight SysML proxies.

### Supported diagram types

| Flag | Mermaid type | SysML proxy |
|---|---|---|
| `bdd` | `classDiagram` | Block Definition Diagram |
| `seq` | `sequenceDiagram` | Sequence Diagram |
| `state` | `stateDiagram-v2` | State Machine Diagram |
| `auto` | Claude infers | Best fit for description |

### Usage

**Auto-infer type (recommended for first pass):**

```bash
python3 -m tools.tool4_mermaid --text "The C2 Ground Station consists of an Operator Console, a Communications Manager..."
```

**Specify diagram type:**

```bash
python3 -m tools.tool4_mermaid --text "..." --type bdd
python3 -m tools.tool4_mermaid --text "..." --type seq
python3 -m tools.tool4_mermaid --text "..." --type state
```

**From a text file:**

```bash
python3 -m tools.tool4_mermaid --file subsystem_description.txt --type bdd
```

**Specify output path:**

```bash
python3 -m tools.tool4_mermaid --text "..." --output c2_bdd.md
```

**Interactive mode:**

```bash
python3 -m tools.tool4_mermaid
```

Default output path: `diagram_output.md` in the current working directory.

Output is a markdown file containing the diagram title, type, notes, and a fenced `mermaid` code block ready to paste into Confluence.

---

## File structure

```
se-tools/
  tools/
    tool1_req_analyzer/
      __init__.py
      __main__.py       -- module entry point
      analyzer.py       -- rule-based issue detection and confidence scoring
      rewriter.py       -- Claude API rewrite call
      formatter.py      -- console output and CSV append
      config.py         -- word lists, weights, threshold, field definitions
      cli.py            -- argparse CLI and interactive session loop
    tool3_traceability/
      __init__.py
      __main__.py       -- module entry point
      generator.py      -- Claude API test case generation
      formatter.py      -- console output and CSV append
      config.py         -- model name, output field definitions
      cli.py            -- argparse CLI, reads requirements CSV, writes traceability matrix
    tool4_mermaid/
      __init__.py
      __main__.py       -- module entry point
      generator.py      -- Claude API diagram generation
      formatter.py      -- console output and .md file save
      config.py         -- model name, supported diagram types
      cli.py            -- argparse CLI and interactive session loop
  docs/
  tests/
  .env                  -- API key (gitignored)
  .gitignore
  CLAUDE.md
  README.md
```
