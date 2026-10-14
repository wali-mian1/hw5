# AI Prompts and Refinements

This file records the prompts, instructions, clarifications, and refinements used while completing Homework 5. API keys and other secrets are never recorded here.

## 2026-10-12 — Initial setup instructions

I asked the assistant to:

- Work in the `Homework/HW 5` folder and save all Homework 5 work there.
- Use the screenshots of the assignment as context and a guide to the actual requirements, while using my written explanations as the working instructions for each problem.
- Tell me if my explanation or implementation direction appears to drift from the assignment.
- Work through the approximately nine questions one at a time.
- Create and maintain this `AI_prompts.md` file so the professor and grader can see my prompts, refinements, and instructions.
- Use the `gpt-5.6-luna` model through Portkey for AI calls, with the `PORTKEY_API_KEY` loaded from the course-root `.env` file and never exposed in source code or logs.
- Keep the work organized.
- Confirm that the provided data ZIP was completed and that the extracted database is accessible.

The assignment screenshots establish the scenario as “Homework 5: Campus Customs Multi-Agent Operations.” The project will involve an MCP server, a FastAPI backend with a fully connected multi-agent team, and a React dashboard. The agents include Boss, Inventory, Accounting, Facilities, and Customer Service. The database contains tables including `desk`, `tickets`, `inventory`, `pricing`, `vendors`, `leases`, `cash_accounts`, `payments`, and `invoices`.

The assignment data setup requires preserving `data/campus_customs.db` as the original database and using `data/campus_customs_new.db` as the working copy. Human approval is required for payments, negative cash balances are forbidden, customer/vendor communications remain drafts, and the database should be reset before a full resolution run.

## Working conventions

- Add each future user problem statement under a dated section.
- Record meaningful prompt refinements and corrections, not secrets.
- Keep the assignment’s one-problem-at-a-time workflow.

## 2026-10-12 — Problem 1 initial explanation

I provided screenshots for Problem 1, “Vibe coder prompts,” and explained that I believe it is only the setup part of the assignment.

The screenshots indicate that this problem requires one section per problem in this log, including the problem number and title, at least one prompt written in the student’s own words, and a follow-up prompt if needed with one sentence explaining what was missing from the first prompt. The screenshots also instruct the AI not to do the problem until the student first asks in their own words what they want done.

The assistant acknowledged that interpretation and asked me to type the exact Problem 1 task in my own words before implementation.

## Problem 1 — Vibe coder prompts

### Student prompt

Because Problem 1 is just setup, ignore the pink instructional text and read the assignment requirements directly, then do what the problem asks.

In my own words, the task is to set up and maintain this `AI_prompts.md` file as a record of the prompts and refinements used for the Homework 5 problems. The file should contain a section for each problem, with the problem number and title, at least one prompt written in my own words, and a follow-up prompt with an explanation when a follow-up is needed.

### Follow-up prompt

Not needed for the setup task.

### Completion note

The prompt log was created at the start of the assignment and now includes this Problem 1 section. No application code or database changes are required for Problem 1.

## 2026-10-12 — Problem 2 prompt

### Student prompt

Open the database and inspect it and all its fields, then copy the original file to `data/campus_customs_new.db`. Later questions will update that working copy. Also study the three open tickets to see their links to other tables.

Start a harness file as listed. List the fields and one short line explaining why each table matters for the agents. This file will continue to grow.

### Follow-up prompt

Not needed; the database, ticket relationships, and initial harness requirements were sufficiently specified.

### Completion note

Reset `data/campus_customs_new.db` from the original database, inspected all nine tables and their fields, reviewed all three open tickets and their linked records, and created `output/harness.md` as the growing database harness reference.

## 2026-10-12 — Problem 3 prompt

### Student prompt

Write an MCP server in `mcp_server/` using FastMCP that talks to `data/campus_customs_new.db`. Do not connect or run it yet. Every agent in Homework 5 will use the tools in this server, and more tools will be added later. For now, write only three clear tools needed for the tickets in the database. Do not invent any data; use only database information.

Update `output/harness.md` with the three MCP tools, including which table each tool reads, which ticket it helps unlock, and a precise sentence explaining why the tool is right for that ticket. Also add a short `mcp_server/README.md` explaining what the server is for and describing the three tools.

### Follow-up prompt

Not needed; the three-tool scope, database path, read-only status, harness requirements, and README requirements were specified clearly.

### Completion note

Created the FastMCP server, README, and detailed harness entries. The three read-only tools are `check_inventory`, `get_invoice_details`, and `get_lease_details`. The server has not been connected or run.

## 2026-10-12 — Problem 4 prompt

### Student prompt

Add the MCP server to this project so the vibe coder can call the tools. Save the connection JSON text in `.mcp.json` at the project root, or use the appropriate local MCP configuration. Once the vibe coder is connected, test each of the three MCP tools. Save the evidence in the listed file. For each tool, include the prompt, tool name, and output, and make sure the output matches values in the database.

### Follow-up prompt

Not needed; the requested MCP connection file, three tool tests, evidence file, and required evidence fields were specified clearly.

### Completion note

Added the project-root `.mcp.json`, pinned the FastMCP-compatible dependency in `requirements.txt`, connected through the MCP stdio protocol, discovered all three tools, and saved exact database-matching results in `output/mcp_smoke.json`. The initial dependency mismatch with MCP 2.x was corrected by pinning MCP below version 2.

## 2026-10-12 — Problem 5 prompt

### Student prompt

Use the assignment’s `gpt-6-luna` model for every agent. Build the Campus Customs agentic team with PydanticAI: Boss, Inventory, Accounting, Facilities, and Customer Service. Include detailed prompts, typed models, and agent loops with full connectivity so the agents can delegate work to one another. Put one prompt file per agent under `backend/prompts/`, put data types in `backend/models.py`, and put the agent files under `backend/`.

Add whatever tools the agents need to the MCP server so they can work on the open tickets. All shop facts must come from the MCP server over `data/campus_customs_new.db`; do not create a second shop-tools layer that bypasses MCP. Wire the agents to append enough information to `output/audit_trail.json` for later auditing, and append rather than wiping the file on each run.

Update `output/harness.md` to list every agent and every MCP tool, with the tables used by each tool. Add a concise safety section covering real-customer and real-money guardrails and token limits. Update `mcp_server/README.md` so its tool list matches the current server.

### Follow-up prompt

Not needed; the team roles, model, file layout, MCP-only data boundary, audit requirements, harness requirements, and safety requirements were specified clearly.

### Completion note

Created five PydanticAI agents with detailed role prompts, shared typed models, full peer delegation, MCP-only shop-data access, append-only audit logging, delegation/request/token limits, and the required safety rules. Added `get_ticket`, `list_open_tickets`, `get_product_pricing`, and `get_cash_balance` to the MCP server. Updated the harness and MCP README to match.

## 2026-10-13 — Problem 6 prompt

### Student prompt

I want to write down what I expect each team to do on the open tickets before wiring the backend. Build `output/desk_tickets.html` so I can double-click it and use one tab each for tickets 101, 102, and 103. Add empty Cash and Reflection tabs for later problems and leave them blank for now.

On each ticket tab, include only an Expected section and leave room for an Actual section to fill after the agents run. For each Expected section, explain in my own words who Boss should call first and why, all the specific agent delegations expected—not just “Boss calls everyone”—and which MCP tools are expected to run. Avoid sending every specialist to every ticket because targeted plans score better.

### Follow-up prompt

Not needed; the page structure, ticket tabs, blank future tabs, expected/actual separation, and targeted planning requirements were clear.

### Completion note

Created the self-contained clickable desk page with targeted expected delegation plans for tickets 101, 102, and 103, reserved Actual sections, and blank Cash and Reflection tabs.

## 2026-10-13 — Problem 7 prompt

### Student prompt

The React frontend dashboard needs a backend it can call. In `backend/main.py`, use FastAPI and add routes that return the three tickets and whether each is resolved or open, run the agent team for a ticket ID, return recent agent events and tool usage for refreshes, approve a payment or purchase only after a human clicks approve, return the current checking balance, and reset the working database to the original values.

Start it from the `backend` folder with `uvicorn main:app --reload --port 8000` so it runs at `http://localhost:8000` for the frontend. In the harness file, list each route in one line and explain what its URL does.

### Follow-up prompt

Not needed; the required route behavior, startup command, port, and harness documentation were clear.

### Completion note

Created the FastAPI backend routes, added MCP-backed ticket/status, event, cash, approval, and reset operations, documented each route in the harness, and made the backend importable using the requested `uvicorn main:app --reload --port 8000` command from the `backend` folder.

## 2026-10-13 — Problem 8 prompt

### Student prompt

Build the frontend dashboard in `frontend/` with React, TypeScript, and Vite. It should call the routes built in Problem 7 and support listing all three tickets, selecting a ticket, starting the agent team, showing agent activity and summaries, marking a ticket resolved after the run, letting a human approve a payment or purchase, and showing the checking balance after an approved payment.

Connect the frontend to `http://localhost:8000`, allow the Vite origin `http://localhost:5173` in the backend, and start the frontend with `npm run dev`. Make the dashboard visually polished and creative, with a black, red, and beige palette, thoughtful transitions, and the feel of a real desk people would want to use. Write `output/design.md` explaining the layout, agent readability, ticket/cash behavior, and creative choices.

### Follow-up prompt

Not needed; the required frontend stack, backend connection, feature list, visual direction, and design-document requirements were clear.

### Completion note

Created the React + Vite + TypeScript dashboard with live ticket polling, agent-run controls, audit activity, resolved-session state, cash display, human approval controls, responsive layout, transitions, and the requested design document.

## 2026-10-13 — Problem 9 full-run prompt

### Student prompt

Before testing the agents on a full run of the three tickets, reset the working database `data/campus_customs_new.db` again so the run starts clean, and note the starting checking balance. Then run all three tickets on the board—101, 102, and 103—until each is resolved.

Open `output/desk_tickets.html` from Problem 6 and, on each ticket tab, fill the Actual section from this run: which agents worked, what they delegated, and which tools they used, while keeping the Expected section for comparison.

On the same HTML file’s Cash tab, itemize the money using the starting balance, each ticket’s cash change and reason, and the ending checking balance. Cash math must be accurate because incorrect cash calculations lose points.

### Current run note

The working database was reset and the starting checking balance was recorded as $3,400.00. The three gpt-6-luna runs completed through the Responses API, and their actual agent/tool results were added to `output/desk_tickets.html`. All three returned `needs_human` rather than resolved: no payment or purchase was authorized, so the ending balance remains $3,400.00. Final resolution artifacts remain pending the required human decisions.

## 2026-10-13 — Problem 10 prompt

### Student prompt

Open `output/desk_tickets.html` and fill the Reflection tab thoroughly and in my own words. Include all of the assignment points: evaluate agent performance on each ticket, compare Actual with Expected for each ticket, explain what would have been simpler with one agent and tools, describe three new Campus Customs problems this team could solve with the tools built, and describe three new problems it could not solve with the current tools plus the agents and tools needed.

Tie every answer to this app and the three tickets that were actually run. Use the ticket tabs and Cash tab as evidence, avoid a generic AI essay, and be specific and complete.

### Follow-up prompt

Not needed; the reflection topics, evidence source, level of detail, and project-specific requirement were clear.

### Completion note

Filled the Reflection tab with detailed ticket-by-ticket performance analysis, Expected-versus-Actual comparisons, single-agent tradeoffs, solvable and unsolvable future problems, required tool/agent extensions, and exact cash-run evidence.

## 2026-10-14 — Problem 11 final-submission prompt

### Student prompt

Problem 11 is only creating the final version needed for submission. Ignore the pink instructions and follow the screenshot exactly. Prepare the public-GitHub submission package, including the expected file layout, both database files, prompt log, requirements, `.env.example`, `.gitignore`, `.mcp.json`, README, MCP server, frontend, backend, prompts, and output evidence. Do not include the real `.env`. Put the repository URL in `output/github_url.txt`.

### Completion note

Prepared the final local submission package with README, `.env.example`, `.gitignore`, output evidence files, honest full-run results, and the existing application files. No public GitHub repository URL or remote was configured, so no URL was invented; `output/github_url.txt` clearly identifies that final manual publishing step.
