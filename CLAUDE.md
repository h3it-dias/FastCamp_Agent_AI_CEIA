# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is a coursework/lab repository for the FastCamp Agent AI (CEIA) course. It is **not a single application** — it's a collection of independent, self-contained exercises and one capstone project, each exploring a different agent-building pattern with Google's Agent Development Kit (ADK). There is no shared build system, root package, or top-level entrypoint; every subfolder is its own Python project with its own dependencies.

When working in this repo, always `cd` into the specific subfolder you're editing before running anything — commands (`uvicorn`, `streamlit run`, `python`, `adk web`) are meant to be run from within that subfolder, and imports/relative paths assume that working directory.

## Repository layout

| Folder | What it is |
|---|---|
| `projeto_final/` | **Capstone project — TIVS** (Triagem Inteligente e Visual de Saúde). A multi-agent medical triage system: FastAPI backend + Streamlit UI + WAHA/n8n WhatsApp integration + Qdrant vector search. See `projeto_final/README.md` for full architecture, setup, and API docs. |
| `Desafio/` | Earlier/simpler iteration of the same triage-agent idea (`agents.py`, `embedding.py`, `interface_grafica.py`) — a challenge exercise, not the final system. |
| `Multi_Agents_ADK/` | ADK "manager + sub_agents" pattern exercises (`Multi_agent_adk_aula` and `_pratica`), run via `adk web` / `adk run`, not FastAPI. |
| `adk_streamlit_aula/`, `adk_streamlit_pratica/` | Multi-agent-over-A2A exercises: a Streamlit UI talks to a `host_agent`/`orquestrador_agent`, which in turn calls independent FastAPI micro-agents over HTTP using a shared `common/a2a_client.py` / `common/a2a_server.py` protocol. |
| `ADK_WAHA/` | Standalone single-file example (`agent.py`) of an ADK agent exposed via FastAPI and driven by WhatsApp (WAHA) messages. |
| `Agent_ReAct_*.ipynb`, `Agents_ADK/`, `Embedding/`, `Pydantic/` | Jupyter notebooks from individual course lessons/practicals — read/run in Jupyter, not part of any app. |
| `docker-compose.yml`, `sessions/`, `n8n_data/` (root) | WAHA + n8n containers used for WhatsApp integration testing across the ADK_WAHA / projeto_final exercises. |

## Common architecture pattern (ADK agents)

Nearly every non-notebook exercise follows the same shape, built on `google-adk`:

- **Agents** are `google.adk.agents.Agent` instances, each with a `name`, `model` (usually via `google.adk.models.lite_llm.LiteLlm(...)`, e.g. `"mistral/mistral-medium-latest"`, `"groq/llama-3.1-8b-instant"`), a natural-language `instruction`, and optionally `sub_agents=[...]` and/or `tools=[...]`.
- **Orchestrator agents** (`orquestrador_agent`, `manager`, `host_agent`, `gerente_agent`) never do the task themselves — their instruction explicitly delegates to sub-agents/tools and forbids answering directly.
- **Execution** goes through `google.adk.sessions.InMemorySessionService` + `google.adk.runners.Runner`. Session/user IDs are created per request (e.g. `f"sessao_{user_id}"`), and responses are read by iterating `runner.run_async(...)` until `event.is_final_response()`.
- **Two ways sub-agents are wired together**, depending on the exercise:
  - *In-process*: `sub_agents=[agent_a, agent_b]` on the parent `Agent` (used in `projeto_final`, `Multi_Agents_ADK`, `ADK_WAHA`).
  - *Over HTTP (A2A)*: each sub-agent runs as its own FastAPI service (`common/a2a_server.py`'s `create_app(agent)` exposes `POST /run`), and the caller uses `common/a2a_client.py` to reach it — used in `adk_streamlit_aula` / `adk_streamlit_pratica`. Each agent folder has a `.well-known/agent.json` describing it and its own `__main__.py` to launch it standalone on its own port.
- **FastAPI is the transport** wherever there's an HTTP boundary — a thin layer that builds a `Content`/`Part` message from `google.genai.types` and forwards it into a `Runner`.
- **Streamlit is the human-facing UI** wherever one exists (`travel_ui.py`, `estudos_ui.py`, `projeto_final/interface.py`, `Desafio/interface_grafica.py`) — it calls the FastAPI layer over HTTP, it does not import agents directly.
- Vector search (in `projeto_final` and `Desafio`) uses Qdrant (`qdrant-client`) with `mistral-embed` (1024-dim) embeddings, chunking `train.txt` into ~200-word chunks via `embedding.py`.

## Running things

Each subfolder needs its own virtualenv/dependency install — there is no single root install step. Pattern for any given exercise:

```bash
cd <exercise-folder>              # e.g. projeto_final, Desafio, adk_streamlit_pratica
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Then, depending on the exercise:

- **FastAPI + Streamlit exercises** (`projeto_final`, `ADK_WAHA`-style, `Desafio`): run the API and UI in separate terminals.
  ```bash
  uvicorn api:app --reload            # backend (adjust module name per folder, e.g. api.py)
  streamlit run interface.py          # UI (adjust filename per folder)
  ```
- **A2A multi-service exercises** (`adk_streamlit_aula`, `adk_streamlit_pratica`): launch each sub-agent as its own process, then the UI.
  ```bash
  python -m agents.<name>_agent          # once per sub-agent, each on its own port (see __main__.py)
  streamlit run travel_ui.py             # or estudos_ui.py
  ```
- **ADK manager/sub_agents exercises** (`Multi_Agents_ADK`): use the ADK CLI from inside the exercise's parent folder.
  ```bash
  adk web        # or: adk run <agent_module>
  ```
- **WhatsApp integration** (root `docker-compose.yml`, used by `ADK_WAHA` and `projeto_final`): `docker compose up` starts WAHA (port 3000) and n8n (port 5678); n8n forwards WhatsApp messages to the exercise's `/webhook`/`/run` endpoint.
- **Notebooks**: open directly in Jupyter; no other setup beyond each folder's dependencies.

There is no test suite, linter, or CI configuration in this repository — validate changes by running the relevant exercise's API/UI manually.

## Environment variables

Each exercise that talks to external services expects its own `.env` (not committed — `.gitignore` excludes `.env`, `venv/`, `__pycache__/`, `sessions/`, `n8n_data/`). Common keys, per `projeto_final/README.md`:

```env
MISTRAL_API_KEY=...
QDRANT_URL=...
QDRANT_API_KEY=...
```

Other exercises may additionally need `OPENAI_API_KEY` or `GROQ_API_KEY` depending on which `LiteLlm(...)` model string they reference.

## Conventions to preserve

- Agent instructions, variable names, and Streamlit UI copy in `projeto_final`/`Desafio` are written in Portuguese (pt-BR) — match that language when editing those files.
- Orchestrator instructions are deliberately strict about delegation ("NUNCA tente diagnosticar sozinho", "Sempre utilize os sub-agentes") — preserve that pattern when adding new sub-agents rather than letting the orchestrator do work itself.
- `projeto_final` is the actively maintained capstone; `Desafio` is a superseded earlier version of the same concept — don't assume changes should be mirrored between them.
