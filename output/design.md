# Campus Customs Agent Desk — Dashboard Design

## Visual direction

The dashboard uses a warm, editorial operations-desk aesthetic rather than a generic admin panel. The palette is near-black for the workspace, parchment beige for human approval actions, muted red/coral for active decisions, and restrained gold/green signals for cash and healthy status. A subtle paper-grain texture and serif display type make the interface feel like a physical desk log, while the monospace labels make operational metadata easy to scan.

## Layout

- The header establishes the shop name, live connection state, and backend address.
- The hero area gives the operator a single-line shift context and a compact “shop status” stamp.
- The metric strip surfaces the open queue, local resolved count, checking balance, and agent signal without making the operator hunt for them.
- The left column is the queue: three compact ticket cards, then a distinct Human Gate card for payment or purchase approvals.
- The right column is the decision workspace: the selected ticket’s facts and start button sit above the live audit trail.
- The responsive layout collapses into a single vertical desk on smaller screens so the selected ticket remains primary.

## How the agents read differently

The activity trail uses a timeline rather than a generic chat box. Each event begins with the agent role in a small uppercase label, followed by either the agent’s summary or the exact MCP tool it queried. That makes Boss, Inventory, Accounting, Facilities, and Customer Service visually distinguishable through their role labels and lets a human follow the handoffs in order. The dashboard does not pretend that a tool call is an agent decision: tool queries and agent results are rendered as different event types.

## Ticket and cash behavior

Each ticket card shows its ID, requester, subject, and open/resolved state. Selecting a card changes the detailed workspace without losing the queue. Starting a run disables the button, shows a working spinner, and polls the backend audit feed so the operator can see activity arrive. When the run completes, that ticket is marked resolved in the desk session and the completed trail remains visible for review.

Cash is deliberately prominent but visually separate from the ticket queue. The checking balance is shown in a gold-toned metric, and every approval lives in the parchment Human Gate card. The form requires a payment type, amount, reference when applicable, and approver name; the backend remains the final guard against insufficient funds. This separation makes “an agent recommended it” visibly different from “a human released the money.”

## Creative choices and usability rationale

The page uses small motion moments—live pulse, ticket hover lift, run spinner, and short alert entrance—to signal changing state without making the desk feel noisy. Coral is reserved for action, green for resolved/healthy state, and gold for money, so color carries meaning consistently. The large serif headlines give the shop a recognizable identity while the dense facts and event metadata remain compact enough for a real operator to scan during a busy shift.

The browser talks to `http://localhost:8000`; the FastAPI backend permits the Vite origin at `http://localhost:5173`. The frontend does not access SQLite or invent shop facts: tickets, balances, events, and actions all flow through the backend routes and MCP-backed services.
