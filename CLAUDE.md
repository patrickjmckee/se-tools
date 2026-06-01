# ASI Systems Engineering - Project Context

## Role & Organization

- **Role:** Systems Engineer - Software Applications IV (Level 4)
- **Company:** Autonomous Solutions, Inc (ASI), Cache County, UT
- **Domain:** Command-and-control software for autonomous and robotic systems
- **Contract:** Long-term (2-3+ years), hybrid/remote
- **Manager/Lead:** Dallon (created the SE function from scratch at ASI)

---

## My Background (Patrick McKee)

- 15+ years systems engineering, industrial automation, DoD programs
- Strong: requirements engineering, ICD, HIL/FAT/SAT, REST/gRPC/MQTT, IIoT, AI-ML deployment
- Current gap to close: MBSE/SysML formalism, Jama-specific workflows
- Stack: Python, JavaScript/TypeScript, Node.js, C/C++, React, SQL
- AI/ML: PyTorch, TensorFlow, SageMaker, Azure AI, LSTM, BERT, CNN

---

## ASI Toolchain

| Tool | Purpose | Notes |
|---|---|---|
| Jama | Requirements management | Document-centric, "old-school"; Dallon wants to move to MBSE/SysML |
| GitHub | Version control | Recently migrated from BitBucket; supports multi-user DVC |
| Jira | Issue tracking | Still in active use |
| Confluence | Collaboration and documentation | Primary doc platform |
| Claude Enterprise | AI assistant | Everyone uses it; AI not yet in product |

---

## Requirements Engineering Standards

### Requirement Quality Criteria (per interview Q1)
A well-formed requirement must be:
- **Quantified** - no vague terms (bad, safe, slow, adequate)
- **Bounded** - relative to a defined baseline (50% of max operational speed, not "slower")
- **Specific** - operating environment, location, sensor availability defined
- **Testable** - linked to a measurable condition or sensor state
- **Traceable** - linked to a stakeholder need and a verification method

### Bad Requirement Anti-Patterns
- Vague adjectives: bad, safe, adequate, sufficient, fast, slow
- Relative terms without baseline: "reduce speed," "increase accuracy"
- Undefined conditions: "if weather is bad," "when needed"
- Ambiguous scope: "the system should," "the system may"

### Requirement Rewrite Pattern
1. Identify stakeholder need
2. Ask clarifying questions: operating environment, sensor availability, baseline values, location constraints
3. Rewrite using: measurable trigger condition + shall statement + quantified threshold

**Example (from ASI interview):**
- Bad: "If the weather is bad the autonomous vehicle must slow down to be safe enough."
- Good: "If there is >= 30% chance and >= 1 inch precipitation forecast in the next 24 hours, or any slippage is detected, then the autonomous vehicle shall reduce maximum speed to 50% of normal operational maximum speed."

### Requirement Types
- **Functional:** what the system shall do
- **Non-functional:** performance, safety, reliability, latency, availability constraints
- **Interface:** data formats, protocols, timing, error handling between subsystems

### Applicable Standards
- ISO 26262 - functional safety (road vehicles)
- IEC 61508 - functional safety (industrial)
- IEC 62061 - safety of machinery
- ISO/IEC 29148 - requirements engineering
- ISO 9001 - quality management
- ISO 14971 - risk management (medical, applicable by analogy)

---

## Verification & Validation

### Verification Methods (per requirement type)
| Method | Use When |
|---|---|
| Test | Measurable output, pass/fail threshold |
| Analysis | Mathematical or model-based proof |
| Inspection | Visual or document-based confirmation |
| Demonstration | Functional behavior shown in operation |

### V&V Traceability Rule
- Every requirement has exactly one or more verification methods assigned
- Every test traces back to at least one requirement
- No orphan tests; no unverified requirements

### Test Types at ASI
- **HIL (Hardware-in-the-Loop):** simulated hardware signals with real software
- **FAT (Factory Acceptance Testing):** at ASI facility before delivery
- **SAT (Site Acceptance Testing):** at customer site after delivery

---

## Interface Control Documents (ICDs)

### Standard ICD Sections
1. Purpose and scope
2. Subsystem descriptions (provider / consumer)
3. Interface definition (protocol, message format, data types, units)
4. Timing and sequencing
5. Error handling and fault behavior
6. Change history

### Protocols Used at ASI
- **REST APIs** - off-board, HTTP-based command/query
- **gRPC** - high-performance, strongly typed RPC between services
- **MQTT** - lightweight pub/sub for telemetry and IoT messaging

---

## MBSE / SysML (Strategic Opportunity)

Dallon wants to move from Jama's document-centric approach to MBSE/SysML.
No one at ASI is currently driving this. This is a differentiation opportunity.

### Key SysML Diagram Types
| Diagram | Purpose |
|---|---|
| Block Definition Diagram (BDD) | Define system structure and component relationships |
| Internal Block Diagram (IBD) | Show subsystem interconnections and interfaces |
| Sequence Diagram | Capture message flows between components over time |
| Use Case Diagram | Capture stakeholder interactions with system |
| State Machine Diagram | Define system behavioral states and transitions |

### Mermaid for Confluence
Mermaid diagrams render natively in Confluence. Use as a lightweight SysML proxy until formal tooling is adopted.

```
classDiagram  -- approximates BDD
sequenceDiagram  -- sequence flows
stateDiagram-v2  -- state machines
```

---

## Communication Patterns

### With Dallon
- He built SE from scratch; respects engineers who think iteratively and revisit stakeholder pools
- Prefers engineers who surface risks early with options, not just problems
- Wants MBSE/SysML direction but hasn't mandated tooling yet
- Receptive to AI tooling discussion; knows ASI has Claude Enterprise

### Stakeholder Interaction Pattern (from interview Q1)
Good SE practice = treat requirements sessions like structured interviews:
- Ask clarifying questions before rewriting
- Identify what sensors/data sources exist vs. what could be added
- Identify operating environment constraints (location, conditions, edge cases)
- Surface assumptions explicitly before committing to a requirement

### Handling Scope Changes (from interview Q3)
When unplanned requirements appear:
1. Identify current known performance baseline
2. Map risks using DFMEA / risk matrix
3. Pareto: flag items with >10% cost or risk increase
4. Run trade-off analysis
5. Present options, risks, and trade-offs to stakeholders -- never commit without a plan

---

## Output Formats

### Requirements
- ID: REQ-[SUBSYSTEM]-[NNN]
- Text: "[Subject] shall [action] [measurable condition]"
- Rationale: one sentence
- Verification method: Test | Analysis | Inspection | Demonstration
- Linked standard: ISO/IEC reference if applicable
- Status: Draft | Review | Approved | Verified

### Jama Import Format (CSV target)
Fields: ID, Name, Description (shall statement), Rationale, Verification Method, Linked Standard, Status

---

## Project Goals This Week

1. Build Requirements Quality Analyzer (stakeholder input -> flagged issues + IEEE rewrite)
2. Build Jama-ready requirement formatter (outputs importable CSV/JSON)
3. Build Test Traceability Matrix Generator (requirements -> test cases + verification method)
4. Build Mermaid SysML diagram generator (subsystem description -> BDD or sequence diagram)
5. Maintain this CLAUDE.md as living context; update with ASI-specific info learned in week 1

---

## Notes to Self

- Do not surface tools on day 1. Use them privately to ramp up, then introduce naturally.
- Mermaid + Confluence is the wedge for MBSE conversation with Dallon.
- ASI has Claude Enterprise -- internal tool pitch is viable once credibility is established.
- MCP server experience is an asset; relevant if ASI wants to integrate Claude into workflows.
