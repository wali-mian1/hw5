# Campus Customs MCP Server

This FastMCP server provides the read-only database tools used by the Campus Customs multi-agent team. It reads the working database at `data/campus_customs_new.db`. The original `data/campus_customs.db` is never used for live work and remains available as a reset source.

The server is intentionally not connected or run as part of Problem 3. Later problems will connect agents to these tools and add more tools as needed.

## Tools

The server currently exposes ten tools. Read-only shop facts and guarded human-approved mutations both stay behind this server:

### `check_inventory(sku, size)`

Reads `inventory` and returns the matching product name, SKU, size, quantity, and location. It supports ticket 101’s request for a Bulldog tee in size S and ticket 103’s request for 20 navy hoodies in size M.

### `get_invoice_details(invoice_id)`

Reads `invoices` and `vendors` and returns the invoice amount, due date, status, description, vendor, specialty, and lead time. It supports ticket 101, whose linked invoice must be checked before deciding how to handle the out-of-stock tee and vendor restock.

### `get_lease_details(lease_id)`

Reads `leases` and returns the shop space, landlord, rent amount, next due date, and notes. It supports ticket 102, whose linked lease contains the rent obligation.

### `get_ticket(ticket_id)`

Reads `tickets` and returns one work-queue record. Every agent uses it to ground its work in the actual requester, subject, identifiers, links, status, notes, and creation time.

### `list_open_tickets()`

Reads `tickets` and returns the current open-ticket queue. Boss uses it to start a run without inventing ticket IDs.

### `list_tickets()`

Reads `tickets` and returns every ticket so the dashboard can show whether each ticket is open or resolved.

### `get_product_pricing(sku)`

Reads `pricing` and returns the unit cost and list price. Inventory and Accounting use it for shortage, margin, and discount analysis for ticket 103.

### `get_cash_balance(account)`

Reads `cash_accounts` and returns the recorded balance and date. Accounting uses it to check cash before proposing any payment.

### `approve_payment(kind, ref_id, amount, account, approved_by)`

This is the only cash-changing tool. It refuses non-positive amounts, missing accounts, and payments larger than the recorded balance. After a human approval reaches the backend, it records the payment in `payments`, subtracts from `cash_accounts`, and marks an invoice paid when the payment kind is `invoice`.

### `reset_database()`

Restores `data/campus_customs_new.db` from the untouched `data/campus_customs.db` so a fresh run can begin.

## Database behavior

All queries are parameterized and read-only. The tools return only records found in the working database; they do not invent products, quantities, vendors, invoices, leases, or other shop data.
