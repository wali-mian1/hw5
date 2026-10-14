# Campus Customs Database Harness

This is the initial database reference for the multi-agent team. The working database is `data/campus_customs_new.db`; `data/campus_customs.db` is the untouched reset copy. The shop date in `desk.date_today` is `2026-08-31`.

## Tables and fields

### `desk`

| Field | Type | Key/constraint |
|---|---|---|
| `date_today` | TEXT | NOT NULL |
| `notes` | TEXT | — |

Why it matters: The shared shop date lets agents determine what invoices, rent, and other obligations are overdue.

### `tickets`

| Field | Type | Key/constraint |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `type` | TEXT | NOT NULL |
| `requester` | TEXT | NOT NULL |
| `subject` | TEXT | NOT NULL |
| `sku` | TEXT | — |
| `size` | TEXT | — |
| `qty` | INTEGER | — |
| `lease_id` | INTEGER | FOREIGN KEY to `leases.id` |
| `invoice_id` | INTEGER | FOREIGN KEY to `invoices.id` |
| `status` | TEXT | NOT NULL |
| `notes` | TEXT | — |
| `created_at` | TEXT | NOT NULL |

Why it matters: Tickets are the work queue that Boss routes to the specialist agents and the place where resolutions and customer-facing drafts remain tracked.

### `inventory`

| Field | Type | Key/constraint |
|---|---|---|
| `sku` | TEXT | Part of composite PRIMARY KEY (`sku`, `size`) |
| `name` | TEXT | NOT NULL |
| `size` | TEXT | Part of composite PRIMARY KEY (`sku`, `size`); NOT NULL |
| `qty` | INTEGER | NOT NULL |
| `location` | TEXT | NOT NULL |

Why it matters: Inventory uses SKU, size, and quantity to check availability, identify shortages, and plan restocking.

### `pricing`

| Field | Type | Key/constraint |
|---|---|---|
| `sku` | TEXT | PRIMARY KEY |
| `unit_cost` | REAL | NOT NULL |
| `list_price` | REAL | NOT NULL |

Why it matters: Accounting and Boss use cost and list price to evaluate margins and reason about discount requests.

### `vendors`

| Field | Type | Key/constraint |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `name` | TEXT | NOT NULL |
| `specialty` | TEXT | NOT NULL |
| `lead_days` | INTEGER | NOT NULL |

Why it matters: Inventory uses vendor specialties and lead times to choose a restocking source, while Accounting checks vendor payment status.

### `leases`

| Field | Type | Key/constraint |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `space_name` | TEXT | NOT NULL |
| `landlord` | TEXT | NOT NULL |
| `monthly_rent` | REAL | NOT NULL |
| `next_due` | TEXT | NOT NULL |
| `notes` | TEXT | — |

Why it matters: Facilities uses lease details to handle rent and shop-space obligations, and Accounting uses them to prepare payment requests.

### `cash_accounts`

| Field | Type | Key/constraint |
|---|---|---|
| `name` | TEXT | PRIMARY KEY |
| `balance` | REAL | NOT NULL |
| `date` | TEXT | NOT NULL |

Why it matters: Accounting checks available cash before proposing payments and must prevent negative balances.

### `payments`

| Field | Type | Key/constraint |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `kind` | TEXT | NOT NULL |
| `ref_id` | INTEGER | — |
| `amount` | REAL | NOT NULL |
| `account` | TEXT | NOT NULL |
| `paid_at` | TEXT | NOT NULL |
| `approved_by` | TEXT | NOT NULL |

Why it matters: Payments are the audit record for approved cash outflows and must only be created after human approval.

### `invoices`

| Field | Type | Key/constraint |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY |
| `vendor_id` | INTEGER | NOT NULL; FOREIGN KEY to `vendors.id` |
| `amount` | REAL | NOT NULL |
| `due_date` | TEXT | NOT NULL |
| `status` | TEXT | NOT NULL |
| `description` | TEXT | — |

Why it matters: Accounting uses invoices to identify unpaid vendor obligations, calculate cash needs, and block vendor orders when an invoice remains open.

## Initial database contents

| Table | Rows |
|---|---:|
| `desk` | 1 |
| `tickets` | 3 |
| `inventory` | 10 |
| `pricing` | 4 |
| `vendors` | 3 |
| `leases` | 1 |
| `cash_accounts` | 1 |
| `payments` | 0 |
| `invoices` | 1 |

## Open-ticket relationships

There are three open tickets:

1. **Ticket 101 — customer order:** Tauhid Zaman requests one `CC-TEE-WHITE`, size `S`. It links to invoice `501`, which is an open $840 vendor invoice for a rush reprint of that same SKU and size. Inventory shows zero units of this tee in size S, so this ticket connects `tickets`, `inventory`, `invoices`, `vendors`, and potentially `pricing` for cost/margin reasoning.
2. **Ticket 102 — rent notice:** Elm City Properties reports rent due in two days. It links to lease `1`, the Chapel Street shop lease with $2,400 monthly rent due on `2026-09-02`. This connects `tickets`, `leases`, `cash_accounts`, and potentially `payments`.
3. **Ticket 103 — price override:** Yale AI Club requests 20 `CC-HOOD-NAVY` hoodies in size M at a bulk discount. Inventory has 8 units in that size, and pricing lists a $22 unit cost and $58 list price. This connects `tickets`, `inventory`, and `pricing`; `vendors` becomes relevant if the shortfall requires restocking.

## Relationships observed

- `tickets.lease_id` references `leases.id`.
- `tickets.invoice_id` references `invoices.id`.
- `invoices.vendor_id` references `vendors.id`.
- `inventory` uses repeated SKU values across sizes, so SKU plus size identifies a stock variant in practice.
- `payments.ref_id` is a polymorphic reference used with the payment `kind`; it has no declared foreign key in the source schema.

## Problem 3 MCP tools

The initial MCP server is in `mcp_server/server.py`. It uses FastMCP and reads only `data/campus_customs_new.db`. The server is not connected or run yet.

### `check_inventory(sku, size)`

- **Tables read:** `inventory`
- **Tickets unlocked:** 101 and 103
- **Why this is the right tool:** Ticket 101 requires checking whether the requested Bulldog tee is available in size S, while ticket 103 requires comparing the requested 20 navy hoodies in size M with the quantity actually in stock; SKU plus size identifies the inventory variant.

### `get_invoice_details(invoice_id)`

- **Tables read:** `invoices`, joined to `vendors`
- **Ticket unlocked:** 101
- **Why this is the right tool:** Ticket 101 links to invoice 501, so the agents need the invoice status and amount plus the vendor’s identity and lead time before deciding how the tee shortage can be handled; the shop rule also blocks new vendor shipments while the invoice is open.

### `get_lease_details(lease_id)`

- **Tables read:** `leases`
- **Ticket unlocked:** 102
- **Why this is the right tool:** Ticket 102 links to lease 1, so Facilities and Accounting need the authoritative landlord, rent amount, and next due date to handle the rent notice.

The server tools are deliberately read-only for this problem. Later problems can add tools for pricing, cash, payments, ticket updates, and other operations.

## Problem 5 agent team and expanded MCP tools

### Agent roles

All five agents use PydanticAI with the `gpt-6-luna` model through Portkey. Each agent has the same MCP read tools and can delegate to every other role through the typed `AgentResult` interface. Prompt files are in `backend/prompts/`.

| Agent | Responsibility | MCP tables used through tools |
|---|---|---|
| **Boss** | Reads and routes tickets, coordinates specialists, resolves conflicts, and makes the final recommendation. | `tickets`, plus any table needed by delegated work |
| **Inventory** | Checks exact SKU-and-size stock, identifies shortages, evaluates pricing and vendor lead-time constraints. | `tickets`, `inventory`, `pricing`, `invoices`, `vendors` |
| **Accounting** | Reviews invoices, cash, rent, costs, margins, and payment or discount approval needs. | `tickets`, `invoices`, `vendors`, `leases`, `pricing`, `cash_accounts` |
| **Facilities** | Handles shop space, lease, landlord, rent amount, and rent timing. | `tickets`, `leases` |
| **Customer Service** | Drafts customer, vendor, landlord, or requester messages without sending them. | `tickets`, plus delegated specialist findings |

### Complete MCP tool list

| MCP tool | Tables read | Primary agent use |
|---|---|---|
| `check_inventory(sku, size)` | `inventory` | Inventory checks ticket 101 and 103 stock by exact SKU and size. |
| `get_invoice_details(invoice_id)` | `invoices`, `vendors` | Accounting and Inventory check ticket 101’s invoice status, vendor, amount, and lead time. |
| `get_lease_details(lease_id)` | `leases` | Facilities and Accounting check ticket 102’s rent obligation. |
| `get_ticket(ticket_id)` | `tickets` | Every agent grounds its work in an authoritative ticket record. |
| `list_open_tickets()` | `tickets` | Boss starts a run from the actual open-ticket queue. |
| `get_product_pricing(sku)` | `pricing` | Inventory and Accounting evaluate ticket 103 cost, list price, margin, and discount bounds. |
| `get_cash_balance(account)` | `cash_accounts` | Accounting checks available cash before proposing any payment. |

The backend contains no direct SQLite shop-data queries. `backend/mcp_client.py` is only an MCP protocol client; all shop facts enter agents through the FastMCP server and the working database.

### Safety and token guardrails

- Agents are advisory and read-only in this problem. No agent can send a customer or vendor message, call a real person, approve a payment, create a purchase order, change cash, or mutate inventory.
- Customer and vendor communications remain drafts on the board until a human approves them.
- Every payment, purchase, discount exception, or other cash-affecting action requires explicit human approval.
- Accounting must check the MCP cash balance and refuse any proposal that would create a negative balance.
- An open unpaid vendor invoice blocks new shipment recommendations from that vendor.
- Agents must cite MCP-returned facts, identify missing data, and escalate instead of guessing.
- Agent delegation is capped at four levels and each run is capped at eight model requests and 2,400 output tokens per agent invocation.
- The audit trail appends `agent_start`, `mcp_tool_call`, and `agent_result` events to `output/audit_trail.json`; prior events are preserved across runs.

## Problem 7 FastAPI backend routes

Run from `Homework/HW 5/backend/` with `uvicorn main:app --reload --port 8000`.

- `GET /health` — confirms that the FastAPI backend is running.
- `GET /tickets` — returns all database tickets and each ticket’s current open/resolved status through MCP.
- `POST /tickets/{ticket_id}/run` — validates the ticket through MCP, then runs Boss and the connected agent team for that ticket.
- `GET /events?limit=50` — returns recent append-only agent and MCP audit events for dashboard refreshes.
- `POST /approve/payment` — applies a human-approved invoice, rent, or purchase payment through the guarded MCP cash tool.
- `POST /approve/purchase` — applies a human-approved purchase through the same guarded MCP cash tool.
- `GET /cash?account=checking` — returns the current cash-account record through MCP.
- `POST /reset` — restores the working database from the untouched original through MCP.

The backend does not open SQLite directly. Reads, cash mutations, and database reset all cross the MCP boundary; the approval routes are the only routes that can request a cash-changing operation.
