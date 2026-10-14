"""Read-only MCP tools for the Campus Customs shop database."""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from mcp.server.fastmcp import FastMCP


DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "campus_customs_new.db"
ORIGINAL_DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "campus_customs.db"

mcp = FastMCP("Campus Customs MCP Server")


def _fetch_one(query: str, parameters: tuple[Any, ...]) -> dict[str, Any]:
    """Run a parameterized read query against the working database."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(query, parameters).fetchone()
    return dict(row) if row is not None else {}


def _fetch_all(query: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Run a parameterized read query and return only database rows."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(query, parameters).fetchall()
    return [dict(row) for row in rows]


@mcp.tool()
def check_inventory(sku: str, size: str) -> dict[str, Any]:
    """Return the inventory record for one SKU and size."""
    return _fetch_one(
        """
        SELECT sku, name, size, qty, location
        FROM inventory
        WHERE sku = ? AND size = ?
        """,
        (sku, size),
    )


@mcp.tool()
def get_invoice_details(invoice_id: int) -> dict[str, Any]:
    """Return an invoice and its vendor details by invoice ID."""
    return _fetch_one(
        """
        SELECT
            invoices.id,
            invoices.vendor_id,
            vendors.name AS vendor_name,
            vendors.specialty AS vendor_specialty,
            vendors.lead_days,
            invoices.amount,
            invoices.due_date,
            invoices.status,
            invoices.description
        FROM invoices
        JOIN vendors ON vendors.id = invoices.vendor_id
        WHERE invoices.id = ?
        """,
        (invoice_id,),
    )


@mcp.tool()
def get_lease_details(lease_id: int) -> dict[str, Any]:
    """Return lease and rent details by lease ID."""
    return _fetch_one(
        """
        SELECT id, space_name, landlord, monthly_rent, next_due, notes
        FROM leases
        WHERE id = ?
        """,
        (lease_id,),
    )


@mcp.tool()
def get_ticket(ticket_id: int) -> dict[str, Any]:
    """Return one ticket from the work queue by ID."""
    return _fetch_one(
        "SELECT * FROM tickets WHERE id = ?",
        (ticket_id,),
    )


@mcp.tool()
def list_open_tickets() -> dict[str, Any]:
    """Return all currently open tickets from the work queue."""
    return {"tickets": _fetch_all("SELECT * FROM tickets WHERE status = 'open' ORDER BY id")}


@mcp.tool()
def list_tickets() -> dict[str, Any]:
    """Return every ticket and its current open or resolved status."""
    return {"tickets": _fetch_all("SELECT * FROM tickets ORDER BY id")}


@mcp.tool()
def get_product_pricing(sku: str) -> dict[str, Any]:
    """Return unit cost and list price for one SKU."""
    return _fetch_one(
        "SELECT sku, unit_cost, list_price FROM pricing WHERE sku = ?",
        (sku,),
    )


@mcp.tool()
def get_cash_balance(account: str) -> dict[str, Any]:
    """Return the current recorded balance for one cash account."""
    return _fetch_one(
        "SELECT name, balance, date FROM cash_accounts WHERE name = ?",
        (account,),
    )


@mcp.tool()
def approve_payment(
    kind: str,
    ref_id: int | None,
    amount: float,
    account: str,
    approved_by: str,
) -> dict[str, Any]:
    """Record a human-approved payment and update the related cash records."""
    if amount <= 0:
        return {"approved": False, "reason": "Payment amount must be positive."}
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        cash = connection.execute(
            "SELECT name, balance, date FROM cash_accounts WHERE name = ?",
            (account,),
        ).fetchone()
        if cash is None:
            return {"approved": False, "reason": "Cash account was not found."}
        if float(cash["balance"]) < amount:
            return {"approved": False, "reason": "Payment refused: insufficient cash."}
        paid_at = datetime.now(timezone.utc).isoformat()
        cursor = connection.execute(
            """
            INSERT INTO payments(kind, ref_id, amount, account, paid_at, approved_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (kind, ref_id, amount, account, paid_at, approved_by),
        )
        new_balance = float(cash["balance"]) - amount
        connection.execute(
            "UPDATE cash_accounts SET balance = ?, date = ? WHERE name = ?",
            (new_balance, cash["date"], account),
        )
        if kind == "invoice" and ref_id is not None:
            connection.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (ref_id,))
        connection.commit()
        return {
            "approved": True,
            "payment_id": cursor.lastrowid,
            "kind": kind,
            "ref_id": ref_id,
            "amount": amount,
            "account": account,
            "new_balance": new_balance,
            "approved_by": approved_by,
        }


@mcp.tool()
def reset_database() -> dict[str, Any]:
    """Reset the working database from the untouched original database."""
    shutil.copy2(ORIGINAL_DATABASE_PATH, DATABASE_PATH)
    return {"reset": True, "database": str(DATABASE_PATH)}


if __name__ == "__main__":
    mcp.run()
