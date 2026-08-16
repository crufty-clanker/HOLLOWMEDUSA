# Agents — Harness × System Prompt × Model Matrix

Each development step in the pipeline is driven by a dedicated agent defined by three components:

| Component | Description |
|-----------|-------------|
| **Harness** | The execution wrapper — how the agent's output is consumed, validated, and passed to the next step. |
| **System Prompt** | The role, constraints, and behavioral instructions injected at every invocation. |
| **Model** | The LLM (and optionally a secondary model for verification) assigned to the step. |

---

## Agent Registry

| Step | Harness | System Prompt | Primary Model | Verification Model |
|------|---------|---------------|---------------|--------------------|
| **1. Requirements** | Extracts structured requirements from user intent; validates completeness against a checklist schema. | "You are a senior product analyst. Decompose vague requests into precise, testable requirements. Output in YAML with fields: goal, scope, constraints, acceptance_criteria." | Fast/cheap (e.g. `gpt-4o-mini`, `claude-haiku`) | — |
| **2. Architecture** | Generates a graph topology (nodes + edges) in JSON; runs a structural validator (cycle detection, reachability). | "You are a distributed systems architect. Design the langgraph topology for the given requirements. Output a directed graph with typed nodes and edge conditions." | Mid-tier (e.g. `gpt-4o`, `claude-sonnet`) | — |
| **3. Prompt Engineering** | Compiles per-node system prompts from templates + context; runs a prompt-lint pass (no contradictions, no dead references). | "You are a prompt engineer specializing in LLM harness design. Write concise, unambiguous system prompts that encode role, output format, and constraints." | Mid-tier | — |
| **4. Code Generation** | Produces Python/TypeScript source for each graph node (tool definitions, state schemas, edge functions). Runs a syntax linter. | "You are a backend engineer. Implement the langgraph nodes, edges, and state management for the architecture. Follow PEP 8 / ESLint strict." | Strong (e.g. `claude-sonnet`, `gpt-4o`) | `gpt-4o-mini` (lint pass) |
| **5. Integration** | Merges generated code into the project; runs the graph in dry-run mode; captures execution traces. | "You are an integration engineer. Wire the generated modules into the langgraph application. Ensure imports resolve, state flows correctly, and edges route as designed." | Strong | — |
| **6. Testing** | Generates unit + integration tests from acceptance criteria; runs them; reports pass/fail per criterion. | "You are a QA engineer. Write tests that cover every acceptance criterion. Use pytest. Assert on exact outputs, state transitions, and error paths." | Strong | `gpt-4o-mini` (test review) |
| **7. Review & Refactor** | Performs a cross-cutting review: security, performance, prompt safety, test coverage. Outputs a diff or approval. | "You are a principal engineer doing a code + prompt review. Identify bugs, security issues, prompt-injection vectors, and performance bottlenecks. Output a structured review report." | Strongest (e.g. `claude-opus`, `gpt-4o`) | — |
| **8. Documentation** | Generates README, API docs, and runbook from the final graph state and code. | "You are a technical writer. Produce clear, runnable documentation: setup instructions, architecture diagram description, API reference, and troubleshooting guide." | Fast/cheap | — |

---

## Harness Details

A **harness** is the thin execution layer around each agent. It handles:

- **Input normalization** — converts prior step output into the expected format.
- **Output validation** — JSON-schema validation, structural checks, lint passes.
- **Retry logic** — exponential backoff with prompt rephrasing on validation failure.
- **Context injection** — attaches relevant prior-step artifacts (requirements → architecture → prompts).
- **Trace capture** — logs prompt, response, tokens, latency, and validation result for every invocation.

### Harness Types

| Type | Use Case |
|------|----------|
| **ExtractHarness** | Parses freeform text into structured data (Requirements). |
| **TopologyHarness** | Validates graph structure (Architecture). |
| **CompileHarness** | Assembles prompts from templates + variables (Prompt Engineering). |
| **CodeHarness** | Generates + lints source code (Code Generation). |
| **MergeHarness** | Integrates code into project tree (Integration). |
| **TestHarness** | Runs tests and aggregates results (Testing). |
| **ReviewHarness** | Cross-cutting analysis with structured output (Review). |
| **DocHarness** | Template-based documentation generation (Documentation). |

---

## Model Assignment Strategy

- **Cost-sensitive steps** (Requirements, Documentation): use the cheapest model that meets quality bar.
- **Quality-sensitive steps** (Architecture, Code Generation, Review): use the strongest model.
- **Verification passes**: use a cheaper model as a secondary check (e.g., lint, test review).
- **Fallback chain**: each agent defines a primary → fallback model list; if the primary fails (rate limit, error), the harness retries with the next model.

---

## Extending

To add a new step:

1. Define a new harness class implementing `Harness.run(input) → validated_output`.
2. Write the system prompt and store it in `prompts/<step>.txt`.
3. Register the agent in `config/agents.yaml` with model assignments.
4. Add the node to the langgraph topology in `config/graph.yaml`.
