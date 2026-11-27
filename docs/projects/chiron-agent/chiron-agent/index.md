# Chiron: a data-analysis agent as a service

<p class="project-meta">Technical assignments · 2026-10</p>

<span class="tag">Python</span> <span class="tag">FastAPI</span> <span class="tag">SQLite</span> <span class="tag">Plotly</span> <span class="tag">Docker</span> <span class="tag">pytest</span> <span class="tag">LLM agents</span> <span class="tag">ReAct</span> <span class="tag">sandboxing</span> <span class="tag">hexagonal architecture</span>

!!! note ""
    The source code is private; get in touch to request access.

You upload a CSV and ask a question in plain language, for example *"Which region earns the most? Show a chart."*
An agent plans, writes Python, runs it in a locked-down process, reads the real output and iterates until it can
answer. The HTTP API returns the answer, an interactive Plotly chart and every step of the reasoning. Sessions are
stored, so a follow-up like *"and which product sells best in that region?"* is understood in context, even after a
restart.

Built as a technical assignment: a complete, tested and containerised service, not a notebook.

## Highlights

- **Agent loop written from scratch** (~170 lines, ReAct: plan, act, observe). No framework, so retries, parse
  recovery and the step budget are explicit and unit-tested. A malformed model reply is fed back as an error, never
  accepted as an answer.
- **Sandbox for generated code**: a fresh process per run with CPU, memory and file-size limits, a scrubbed
  environment, and a Python audit hook that blocks file access outside a temp folder, network, subprocesses and native
  code. A violation kills the process. The container adds the real boundary: non-root, read-only filesystem, no
  capabilities.
- **Hexagonal architecture**: the agent core is plain Python and knows nothing about HTTP, the database or the model
  vendor. A test parses the source tree and fails if that rule is broken. Any OpenAI-compatible model works (Gemini by
  default).
- **About 150 automated tests**: the agent runs against a scripted model (including broken replies and outages), the
  sandbox is attacked for real (memory bombs, `/etc/passwd`, symlinks, `_socket`, fork), and a Docker smoke test checks
  the built image.
- **Robust by design**: retries with backoff on model errors, a concurrency cap that answers `429` instead of running
  out of memory, structured JSON logs with request ids, and every step of every turn saved as it happens.
- **41 documented design decisions**, each with the alternatives considered and the trade-off accepted.

## How it works

```
Client ──► FastAPI ──► AnalysisService ──► ReAct agent ──► LLM (any OpenAI-compatible endpoint)
                              │                   └──────► Sandbox (separate process)
                              └──► SQLite: sessions, messages, traces, plots
```

1. The service validates the request, takes a concurrency slot and opens a turn.
2. The agent sends the model a profile of the dataset, the earlier questions and answers, and the new question.
3. Each reply is a thought plus one Python block, or a final answer. The code runs in the sandbox and its real output
   goes back to the model.
4. Every step is stored as it happens. The response holds the answer, a link to the chart and the full trace.

## Verified on a real run

Running in Docker against Gemini and driven only through the API, the first answer matched an independent
recomputation of the CSV to the cent. The follow-up resolved *"that region"* correctly, and after a container
restart the session carried on with all its messages and the chart still stored. Two transient `503` errors from the
model were retried automatically and the request still succeeded.

## Stack

Python 3.12 · FastAPI · SQLite (WAL) · pandas · Plotly · Docker Compose · pytest · uv
