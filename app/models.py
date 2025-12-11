from sqlalchemy import Column, Integer, String

from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(320), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="active")
    notes = Column(String(500), nullable=True)
