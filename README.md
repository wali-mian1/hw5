# Campus Customs Multi-Agent Operations

Homework 5 builds a Campus Customs operations desk with three layers:

- `mcp_server/` — the FastMCP server. All shop facts and guarded database changes go through this layer.
- `backend/` — the PydanticAI agent team and FastAPI routes.
- `frontend/` — the React + Vite + TypeScript operations dashboard.

The original database is `data/campus_customs.db`. The working database is `data/campus_customs_new.db`. Reset the working copy before a fresh full run; never use the original database for live changes.

## Setup

1. Create and activate the local environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

2. Copy the course-root `PORTKEY_API_KEY` into a local `.env` file according to `.env.example`. Never commit `.env`.

3. Start the MCP server when using MCP clients through the project-root `.mcp.json` configuration.

4. Start the backend from `backend/`:

   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

5. In another terminal, start the React dashboard:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Open `http://localhost:5173`.

## Important operating rules

- Agents use `gpt-6-luna` through Portkey and load `PORTKEY_API_KEY` from the environment.
- Shop facts come through MCP and `data/campus_customs_new.db`; backend agents do not open SQLite directly.
- Customer and vendor messages remain drafts.
- Payments and purchases require human approval and cannot create a negative cash balance.
- Reset the working database before a full three-ticket run.
- The append-only audit trail is `output/audit_trail.json`.

## Evidence

- `output/harness.md` documents tables, tools, agents, routes, dashboard behavior, and safety controls.
- `output/mcp_smoke.json` records the initial three-tool MCP smoke test.
- `output/desk_tickets.html` contains Expected/Actual ticket plans, cash evidence, and the detailed reflection.
- `output/resolved_tickets.json` and `output/resolved_board.html` preserve the honest final state of the recorded run; the run stopped at human-review gates rather than inventing approvals.
- `AI_prompts.md` records the prompts and refinements used throughout the assignment.
