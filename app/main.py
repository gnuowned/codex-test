from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Registry")


@app.get("/")
def healthcheck():
    return {"status": "ok"}


@app.get("/customers", response_model=list[schemas.Customer])
def list_customers(db: Session = Depends(get_db)):
    return crud.list_customers(db)


@app.post(
    "/customers",
    response_model=schemas.Customer,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db, payload)


@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(
    customer_id: int, payload: schemas.CustomerUpdate, db: Session = Depends(get_db)
):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.update_customer(db, customer, payload)


@app.delete(
    "/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    crud.delete_customer(db, customer)
    return None
