import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Route

from . import crud, schemas
from .database import get_connection, init_db

init_db()

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# In-memory users/roles. Passwords can be overridden via env vars.
USERS = {
    "admin": {"password": os.environ.get("ADMIN_PASSWORD", "admin123"), "role": "admin"},
    "capturista": {
        "password": os.environ.get("CAPTURISTA_PASSWORD", "captura123"),
        "role": "capturista",
    },
    "operador": {
        "password": os.environ.get("OPERADOR_PASSWORD", "operador123"),
        "role": "operador",
    },
}


async def auth_user(request: Request) -> Dict[str, str] | JSONResponse:
    """HTTP Basic auth; returns user dict or JSONResponse if unauthorized."""
    header = request.headers.get("authorization")
    if not header or not header.lower().startswith("basic "):
        return JSONResponse(
            {"detail": "authentication required"},
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="auth"'},
        )
    try:
        decoded = base64.b64decode(header.split(" ", 1)[1]).decode()
        username, password = decoded.split(":", 1)
    except Exception:
        return JSONResponse({"detail": "invalid auth header"}, status_code=401)

    user = USERS.get(username)
    if not user or user["password"] != password:
        return JSONResponse({"detail": "invalid credentials"}, status_code=401)
    return {"username": username, "role": user["role"]}


def is_allowed(user: Dict[str, str], allowed_roles) -> bool:
    return user.get("role") in allowed_roles


async def healthcheck(request: Request) -> JSONResponse:
    # Simple liveness check.
    return JSONResponse({"status": "ok"})


async def ui(request: Request):
    # Serve the single-page UI for CRUD actions.
    index_path = STATIC_DIR / "index.html"
    return FileResponse(index_path)


async def profile(request: Request) -> JSONResponse:
    # Return authenticated user info.
    user = await auth_user(request)
    if isinstance(user, JSONResponse):
        return user
    return JSONResponse({"username": user["username"], "role": user["role"]})


async def list_customers(request: Request) -> JSONResponse:
    # Retrieve full customer list.
    user = await auth_user(request)
    if isinstance(user, JSONResponse):
        return user
    if not is_allowed(user, ("admin", "capturista", "operador")):
        return JSONResponse({"detail": "forbidden"}, status_code=403)

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
    user = await auth_user(request)
    if isinstance(user, JSONResponse):
        return user
    if not is_allowed(user, ("admin", "capturista")):
        return JSONResponse({"detail": "forbidden"}, status_code=403)

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
    user = await auth_user(request)
    if isinstance(user, JSONResponse):
        return user
    if not is_allowed(user, ("admin", "capturista", "operador")):
        return JSONResponse({"detail": "forbidden"}, status_code=403)

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
    user = await auth_user(request)
    if isinstance(user, JSONResponse):
        return user
    if not is_allowed(user, ("admin", "capturista")):
        return JSONResponse({"detail": "forbidden"}, status_code=403)

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
    user = await auth_user(request)
    if isinstance(user, JSONResponse):
        return user
    if not is_allowed(user, ("admin",)):
        return JSONResponse({"detail": "forbidden"}, status_code=403)

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
    Route("/ui", ui, methods=["GET"]),
    Route("/auth/profile", profile, methods=["GET"]),
    Route("/customers", list_customers, methods=["GET"]),
    Route("/customers", create_customer, methods=["POST"]),
    Route("/customers/{customer_id:int}", read_customer, methods=["GET"]),
    Route("/customers/{customer_id:int}", update_customer, methods=["PUT"]),
    Route("/customers/{customer_id:int}", delete_customer, methods=["DELETE"]),
]

app = Starlette(debug=False, routes=routes)
