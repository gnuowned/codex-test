from typing import Iterable, Optional

import sqlite3

from . import schemas


def list_customers(conn: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    cur = conn.execute(
        "SELECT id, name, email, phone, status, notes FROM customers ORDER BY id ASC"
    )
    return cur.fetchall()


def get_customer(conn: sqlite3.Connection, customer_id: int) -> Optional[sqlite3.Row]:
    cur = conn.execute(
        "SELECT id, name, email, phone, status, notes FROM customers WHERE id = ?",
        (customer_id,),
    )
    return cur.fetchone()


def create_customer(conn: sqlite3.Connection, payload: schemas.CustomerCreate) -> sqlite3.Row:
    data = payload.validate().__dict__
    cur = conn.execute(
        """
        INSERT INTO customers (name, email, phone, status, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (data["name"], data["email"], data["phone"], data["status"], data["notes"]),
    )
    conn.commit()
    customer_id = cur.lastrowid
    return get_customer(conn, customer_id)


def update_customer(
    conn: sqlite3.Connection, customer_id: int, payload: schemas.CustomerUpdate
) -> Optional[sqlite3.Row]:
    data = payload.validate().__dict__
    fields = []
    values = []
    for field, value in data.items():
        if value is not None:
            fields.append(f"{field} = ?")
            values.append(value)
    if not fields:
        return get_customer(conn, customer_id)
    values.append(customer_id)
    conn.execute(f"UPDATE customers SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    return get_customer(conn, customer_id)


def delete_customer(conn: sqlite3.Connection, customer_id: int) -> bool:
    cur = conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    return cur.rowcount > 0
