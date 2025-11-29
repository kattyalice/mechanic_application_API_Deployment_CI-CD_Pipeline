from application.extensions import db, Base
from sqlalchemy.orm import Mapped, mapped_column
from typing import List

# Many-to-many tables
service_mechanics = db.Table(
    "service_mechanics",
    Base.metadata,
    db.Column("ticket_id", db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id"), primary_key=True),
)

service_ticket_inventory = db.Table(
    "service_ticket_inventory",
    Base.metadata,
    db.Column("ticket_id", db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("inventory_id", db.ForeignKey("inventory.id"), primary_key=True),
)

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(50))
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(
        back_populates="customer",
        cascade="all, delete-orphan"
    )

class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(50))
    salary: Mapped[float] = mapped_column(db.Float)

    tickets: Mapped[List["ServiceTicket"]] = db.relationship(
        secondary=service_mechanics,
        back_populates="mechanics"
    )

class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=0)

    tickets: Mapped[List["ServiceTicket"]] = db.relationship(
        secondary=service_ticket_inventory,
        back_populates="parts"
    )

class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)

    VIN: Mapped[str] = mapped_column(db.String(255), nullable=True)
    service_date: Mapped[str] = mapped_column(db.String(255), nullable=True)
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=True)

    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"))

    customer: Mapped["Customer"] = db.relationship(
        back_populates="service_tickets"
    )

    mechanics: Mapped[List["Mechanic"]] = db.relationship(
        secondary=service_mechanics,
        back_populates="tickets"
    )

    parts: Mapped[List["Inventory"]] = db.relationship(
        secondary=service_ticket_inventory,
        back_populates="tickets"
    )
