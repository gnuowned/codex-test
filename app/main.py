import json
from typing import Any, Dict, List

from sqlalchemy.orm import Session
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from . import crud, models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)


def db_dependency(request: Request) -> Session:
    return next(get_db())


async def healthcheck(request: Request) -> JSONResponse:
    return JSONResponse({\"status\": \"ok\"})


async def list_customers(request: Request) -> JSONResponse:
    db = db_dependency(request)
    customers = crud.list_customers(db)
    result = [
        schemas.Customer(
            id=c.id,
            name=c.name,
            email=c.email,
            phone=c.phone,
            status=c.status,
            notes=c.notes,
        ).dict()
        for c in customers
    ]
    return JSONResponse(result)


async def create_customer(request: Request) -> JSONResponse:
    payload: Dict[str, Any] = await request.json()
    try:
        customer_payload = schemas.CustomerCreate(**payload).validate()
    except Exception as exc:
        return JSONResponse({\"detail\": str(exc)}, status_code=400)

    db = db_dependency(request)
    customer = crud.create_customer(db, customer_payload)
    result = schemas.Customer(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        status=customer.status,
        notes=customer.notes,
    ).dict()
    return JSONResponse(result, status_code=201)


async def read_customer(request: Request) -> JSONResponse:
    customer_id = int(request.path_params[\"customer_id\"])
    db = db_dependency(request)
    customer = crud.get_customer(db, customer_id)
    if not customer:
        return JSONResponse({\"detail\": \"Customer not found\"}, status_code=404)
    result = schemas.Customer(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        status=customer.status,
        notes=customer.notes,
    ).dict()
    return JSONResponse(result)


async def update_customer(request: Request) -> JSONResponse:
    customer_id = int(request.path_params[\"customer_id\"])
    payload: Dict[str, Any] = await request.json()
    try:
        update_payload = schemas.CustomerUpdate(**payload).validate()
    except Exception as exc:
        return JSONResponse({\"detail\": str(exc)}, status_code=400)

    db = db_dependency(request)
    customer = crud.get_customer(db, customer_id)
    if not customer:
        return JSONResponse({\"detail\": \"Customer not found\"}, status_code=404)
    customer = crud.update_customer(db, customer, update_payload)
    result = schemas.Customer(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        status=customer.status,
        notes=customer.notes,
    ).dict()
    return JSONResponse(result)


async def delete_customer(request: Request) -> Response:
    customer_id = int(request.path_params[\"customer_id\"])
    db = db_dependency(request)
    customer = crud.get_customer(db, customer_id)
    if not customer:
        return JSONResponse({\"detail\": \"Customer not found\"}, status_code=404)
    crud.delete_customer(db, customer)
    return Response(status_code=204)


routes = [
    Route(\"/\", healthcheck, methods=[\"GET\"]),
    Route(\"/customers\", list_customers, methods=[\"GET\"]),
    Route(\"/customers\", create_customer, methods=[\"POST\"]),
    Route(\"/customers/{customer_id:int}\", read_customer, methods=[\"GET\"]),
    Route(\"/customers/{customer_id:int}\", update_customer, methods=[\"PUT\"]),
    Route(\"/customers/{customer_id:int}\", delete_customer, methods=[\"DELETE\"]),
]

app = Starlette(debug=False, routes=routes)
