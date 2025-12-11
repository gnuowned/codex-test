from typing import Iterable, Optional

from sqlalchemy.orm import Session

from . import models, schemas


def list_customers(db: Session) -> Iterable[models.Customer]:
    return db.query(models.Customer).order_by(models.Customer.id.asc()).all()


def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def create_customer(db: Session, payload: schemas.CustomerCreate) -> models.Customer:
    data = payload.validate().__dict__
    customer = models.Customer(**data)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(
    db: Session, customer: models.Customer, payload: schemas.CustomerUpdate
) -> models.Customer:
    data = payload.validate().__dict__
    for field, value in data.items():
        if value is not None:
            setattr(customer, field, value)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer: models.Customer) -> None:
    db.delete(customer)
    db.commit()
