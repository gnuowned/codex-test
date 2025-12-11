import json
from typing import Any, Dict

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from . import crud, schemas
from .database import get_connection, init_db

init_db()


async def healthcheck(request: Request) -> JSONResponse:
    # Simple liveness check.
    return JSONResponse({"status": "ok"})


async def list_customers(request: Request) -> JSONResponse:
    # Retrieve full customer list.
    conn = get_connection()
    try:
        customers = crud.list_customers(conn)
        result = [
            schemas.Customer(
                id=row["id"],
                name=row["name"],
                email=row["email"],
                phone=row["phone"],
                status=row["status"],
                notes=row["notes"],
            ).dict()
            for row in customers
        ]
        return JSONResponse(result)
    finally:
        conn.close()


async def create_customer(request: Request) -> JSONResponse:
    payload: Dict[str, Any] = await request.json()
    try:
        customer_payload = schemas.CustomerCreate(**payload).validate()
    except Exception as exc:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    conn = get_connection()
    try:
        # Duplicate email returns 400 with a clear message.
        try:
            customer = crud.create_customer(conn, customer_payload)
        except ValueError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=400)
        result = schemas.Customer(
            id=customer["id"],
            name=customer["name"],
            email=customer["email"],
            phone=customer["phone"],
            status=customer["status"],
            notes=customer["notes"],
        ).dict()
        return JSONResponse(result, status_code=201)
    finally:
        conn.close()


async def read_customer(request: Request) -> JSONResponse:
    customer_id = int(request.path_params["customer_id"])
    conn = get_connection()
    try:
        customer = crud.get_customer(conn, customer_id)
        if not customer:
            return JSONResponse({"detail": "Customer not found"}, status_code=404)
        result = schemas.Customer(
            id=customer["id"],
            name=customer["name"],
            email=customer["email"],
            phone=customer["phone"],
            status=customer["status"],
            notes=customer["notes"],
        ).dict()
        return JSONResponse(result)
    finally:
        conn.close()


async def update_customer(request: Request) -> JSONResponse:
    customer_id = int(request.path_params["customer_id"])
    payload: Dict[str, Any] = await request.json()
    try:
        update_payload = schemas.CustomerUpdate(**payload).validate()
    except Exception as exc:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    conn = get_connection()
    try:
        existing = crud.get_customer(conn, customer_id)
        if not existing:
            return JSONResponse({"detail": "Customer not found"}, status_code=404)
        # Propagate validation or constraint errors as 400.
        try:
            customer = crud.update_customer(conn, customer_id, update_payload)
        except ValueError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=400)
        result = schemas.Customer(
            id=customer["id"],
            name=customer["name"],
            email=customer["email"],
            phone=customer["phone"],
            status=customer["status"],
            notes=customer["notes"],
        ).dict()
        return JSONResponse(result)
    finally:
        conn.close()


async def delete_customer(request: Request) -> Response:
    customer_id = int(request.path_params["customer_id"])
    conn = get_connection()
    try:
        # 204 when deleted, 404 when missing.
        deleted = crud.delete_customer(conn, customer_id)
        if not deleted:
            return JSONResponse({"detail": "Customer not found"}, status_code=404)
        return Response(status_code=204)
    finally:
        conn.close()


routes = [
    Route("/", healthcheck, methods=["GET"]),
    Route("/customers", list_customers, methods=["GET"]),
    Route("/customers", create_customer, methods=["POST"]),
    Route("/customers/{customer_id:int}", read_customer, methods=["GET"]),
    Route("/customers/{customer_id:int}", update_customer, methods=["PUT"]),
    Route("/customers/{customer_id:int}", delete_customer, methods=["DELETE"]),
]

app = Starlette(debug=False, routes=routes)
