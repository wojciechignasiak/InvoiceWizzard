from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, DATE, BOOLEAN, FLOAT, INTEGER, BYTEA
from datetime import datetime
from typing import Optional, List


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False, default=uuid4)
    email: Mapped[str] = mapped_column(VARCHAR(320), nullable=False)
    password: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    street: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    salt: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    registration_date: Mapped[datetime] = mapped_column(DATE, nullable=False)
    last_login: Mapped[datetime] = mapped_column(DATE, nullable=False)
    email_notification: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    push_notification: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)

class UserBusinessEntity(Base):
    __tablename__ = 'user_business_entity'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False, default=uuid4)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    company_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    street: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    nip: Mapped[Optional[str]] = mapped_column(VARCHAR(10), nullable=True)
    krs: Mapped[Optional[str]] = mapped_column(VARCHAR(10), nullable=True)
    invoice_issued: Mapped[List["InvoiceIssued"]] = relationship(back_populates="user_business_entity")
    invoice_recived: Mapped[List["InvoiceRecived"]] = relationship(back_populates="user_business_entity")

class ExternalBusinessEntity(Base):
    __tablename__= 'external_business_entity'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False, default=uuid4)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    company_name: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    street: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    nip: Mapped[Optional[str]] = mapped_column(VARCHAR(10), nullable=True)
    krs: Mapped[Optional[str]] = mapped_column(VARCHAR(10), nullable=True)
    invoice_item: Mapped[List["InvoiceIssuedItem"]] = relationship(back_populates="invoice_issued")
    invoice_issued: Mapped[List["InvoiceIssued"]] = relationship(back_populates="external_business_entity")
    invoice_recived: Mapped[List["InvoiceRecived"]] = relationship(back_populates="external_business_entity")

class InvoiceRecived(Base):
    __tablename__ = 'invoice_recived'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False, default=uuid4)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user_business_entity_id: Mapped[str] = mapped_column(ForeignKey("user_business_entity.id", ondelete="CASCADE"))
    user_business_entity: Mapped["UserBusinessEntity"] = relationship(back_populates="invoice_recived")
    external_business_entity_id: Mapped[str] = mapped_column(ForeignKey("external_business_entity.id", ondelete="CASCADE"))
    external_business_entity: Mapped["ExternalBusinessEntity"] = relationship(back_populates="invoice_recived")
    invoice_pdf: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    invoice_number: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    issue_date: Mapped[Optional[datetime]] = mapped_column(DATE, nullable=True)
    sale_date: Mapped[Optional[datetime]] = mapped_column(DATE, nullable=True)
    net_value: Mapped[Optional[float]] = mapped_column(FLOAT, nullable=True)
    gross_value: Mapped[Optional[float]] = mapped_column(FLOAT, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(VARCHAR(10), nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    payment_deadline: Mapped[Optional[datetime]] = mapped_column(DATE, nullable=True)
    added_date: Mapped[Optional[datetime]] = mapped_column(DATE, nullable=False)
    is_settled: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    is_accepted: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)


class InvoiceRecivedItem(Base):
    __tablename__ = 'invoice_recived_item'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False, default=uuid4)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoice_recived.id", ondelete="CASCADE"), nullable=False)
    invoice_recived: Mapped["InvoiceRecived"] = relationship(back_populates="invoice_item")
    ordinal_number: Mapped[int] = mapped_column(INTEGER, nullable=False)
    item_description: Mapped[Optional[str]] = mapped_column(VARCHAR, nullable=True)
    net_value: Mapped[Optional[float]] = mapped_column(FLOAT, nullable=True)
    gross_value: Mapped[Optional[float]] = mapped_column(FLOAT, nullable=True)
    tax_percent: Mapped[Optional[str]] = mapped_column(VARCHAR(10), nullable=True)


class InvoiceIssued(Base):
    __tablename__ = 'invoice_issued'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False, default=uuid4)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"))
    user_business_entity_id: Mapped[str] = mapped_column(ForeignKey("user_business_entity.id", ondelete="CASCADE"), nullable=False)
    user_business_entity: Mapped["UserBusinessEntity"] = relationship(back_populates="invoice_issued")
    external_business_entity_id: Mapped[str] = mapped_column(ForeignKey("external_business_entity.id", ondelete="CASCADE"), nullable=False)
    external_business_entity: Mapped["ExternalBusinessEntity"] = relationship(back_populates="invoice_issued")
    invoice_pdf: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    invoice_number: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    issue_date: Mapped[Optional[datetime]] = mapped_column(DATE, nullable=True)
    sale_date: Mapped[Optional[datetime]] = mapped_column(DATE, nullable=True)
    net_value: Mapped[Optional[float]] = mapped_column(FLOAT, nullable=True)
    gross_value: Mapped[Optional[float]] = mapped_column(FLOAT, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(VARCHAR(10), nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    payment_deadline: Mapped[Optional[datetime]] = mapped_column(DATE, nullable=True)
    added_date: Mapped[Optional[datetime]] = mapped_column(DATE, nullable=False)
    is_settled: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    is_accepted: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    invoice_item: Mapped[List["InvoiceIssuedItem"]] = relationship(back_populates="invoice_issued")


class InvoiceIssuedItem(Base):
    __tablename__ = 'invoice_issued_item'
    id: Mapped[str] = mapped_column(UUID, primary_key=True, nullable=False, default=uuid4)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoice_issued.id", ondelete="CASCADE"), nullable=False)
    invoice_issued: Mapped["InvoiceIssued"] = relationship(back_populates="invoice_item")
    ordinal_number: Mapped[int] = mapped_column(INTEGER, nullable=False)
    item_description: Mapped[Optional[str]] = mapped_column(VARCHAR, nullable=True)
    net_value: Mapped[Optional[float]] = mapped_column(FLOAT, nullable=True)
    gross_value: Mapped[Optional[float]] = mapped_column(FLOAT, nullable=True)
    tax_percent: Mapped[Optional[str]] = mapped_column(VARCHAR(10), nullable=True)