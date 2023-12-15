from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, DATE, BOOLEAN, FLOAT, INTEGER
from typing import Optional, List
from datetime import date

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(320), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True, unique=True)
    city: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    street: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    salt: Mapped[str] = mapped_column(VARCHAR(400), nullable=False)
    registration_date: Mapped[date] = mapped_column(DATE, nullable=False)
    last_login: Mapped[date] = mapped_column(DATE, nullable=False)
    email_notification: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    push_notification: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)

class UserBusinessEntity(Base):
    __tablename__ = 'user_business_entity'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    company_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    street: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    nip: Mapped[Optional[str]] = mapped_column(VARCHAR(10), nullable=False)
    invoice: Mapped[List["Invoice"]] = relationship(back_populates="user_business_entity")

class ExternalBusinessEntity(Base):
    __tablename__= 'external_business_entity'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    company_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    street: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    nip: Mapped[Optional[str]] = mapped_column(VARCHAR(10), nullable=True)
    invoice: Mapped[List["Invoice"]] = relationship(back_populates="external_business_entity")

class Invoice(Base):
    __tablename__ = 'invoice'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user_business_entity_id: Mapped[str] = mapped_column(ForeignKey("user_business_entity.id", ondelete="CASCADE"))
    user_business_entity: Mapped["UserBusinessEntity"] = relationship(back_populates="invoice")
    external_business_entity_id: Mapped[str] = mapped_column(ForeignKey("external_business_entity.id", ondelete="CASCADE"))
    external_business_entity: Mapped["ExternalBusinessEntity"] = relationship(back_populates="invoice")
    invoice_pdf: Mapped[Optional[str]] = mapped_column(VARCHAR(500), nullable=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    issue_date: Mapped[Optional[date]] = mapped_column(DATE, nullable=True)
    sale_date: Mapped[Optional[date]] = mapped_column(DATE, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(VARCHAR, nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    payment_deadline: Mapped[Optional[date]] = mapped_column(DATE, nullable=True)
    added_date: Mapped[Optional[date]] = mapped_column(DATE, nullable=False)
    is_settled: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    is_accepted: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    is_issued: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    invoice_item: Mapped[List["InvoiceItem"]] = relationship(back_populates="invoice")


class InvoiceItem(Base):
    __tablename__ = 'invoice_item'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoice.id", ondelete="CASCADE"), nullable=False)
    invoice: Mapped["Invoice"] = relationship(back_populates="invoice_item")
    ordinal_number: Mapped[int] = mapped_column(INTEGER, nullable=False)
    item_description: Mapped[Optional[str]] = mapped_column(VARCHAR, nullable=True)
    number_of_items: Mapped[Optional[int]] = mapped_column(INTEGER, nullable=False)
    net_value: Mapped[Optional[float]] = mapped_column(FLOAT, nullable=True)
    gross_value: Mapped[Optional[float]] = mapped_column(FLOAT, nullable=True)