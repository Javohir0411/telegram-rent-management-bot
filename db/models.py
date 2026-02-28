from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    func,
    ForeignKey,
    Date,
    Enum,
    Text,
    Float,
    Boolean,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database.base import Base
from utils.enums import (
    RentStatusEnum,
    ProductTypeEnum,
    PaymentStatusEnum,
    ProductSizeEnum,
)

from sqlalchemy import Column, Integer, String, Float, Date, func
from database.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=True)

    base_latitude = Column(Float, nullable=True)
    base_longitude = Column(Float, nullable=True)

    users = relationship("User", back_populates="tenant")

    created_at = Column(Date, server_default=func.current_date())
    updated_at = Column(Date, server_default=func.current_date(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        # tenant ichida telegram_id unique bo'lsin
        UniqueConstraint("tenant_id", "telegram_id", name="uq_user_tenant_telegram"),
        # tenant ichida phone unique bo'lsin
        UniqueConstraint("tenant_id", "user_phone_number", name="uq_user_tenant_phone"),
    )

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)

    user_fullname = Column(String, nullable=False)
    user_phone_number = Column(String, nullable=False)
    selected_language = Column(String, nullable=False)
    tenant = relationship("Tenant", back_populates="users")
    rents = relationship("Rent", back_populates="user")

    created_at = Column(Date, server_default=func.current_date())
    updated_at = Column(Date, server_default=func.current_date(), onupdate=func.now())


class Renter(Base):
    __tablename__ = "renter"
    __table_args__ = (
        #tenant ichida renter phone unique bo'lsin
        UniqueConstraint("tenant_id", "renter_phone_number", name="uq_renter_tenant_phone"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)

    renter_fullname = Column(String, nullable=False)
    renter_phone_number = Column(String, nullable=False)
    renter_passport_info = Column(String, nullable=True)

    rents = relationship("Rent", back_populates="renter")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        # ✅ tenant ichida bir xil type+size 2 marta yozilmasin
        UniqueConstraint("tenant_id", "product_type", "product_size", name="uq_product_tenant_type_size"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)

    product_type = Column(Enum(ProductTypeEnum, name="product_type_enum"), nullable=False)
    product_size = Column(Enum(ProductSizeEnum, name="product_size_enum"), nullable=True)

    total_quantity = Column(Integer, nullable=False)
    price_per_day = Column(Float, nullable=True)

    rents = relationship("Rent", back_populates="product")


class Rent(Base):
    __tablename__ = "rents"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    renter_id = Column(Integer, ForeignKey("renter.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    returned_quantity = Column(Integer, nullable=False, server_default="0")

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    delivery_needed = Column(Boolean, nullable=True, default=False)
    delivery_price = Column(Float, nullable=True)

    product_price = Column(Float, nullable=True)
    rent_price = Column(Float, nullable=True)

    comment = Column(Text, nullable=False)

    status = Column(Enum(PaymentStatusEnum), nullable=False)
    rent_status = Column(Enum(RentStatusEnum), nullable=False)

    user = relationship("User", back_populates="rents")
    renter = relationship("Renter", back_populates="rents")
    product = relationship("Product", back_populates="rents")

    created_at = Column(Date, server_default=func.current_date())
    updated_at = Column(Date, server_default=func.current_date(), onupdate=func.now())


# Indexlar (qolsin)
Index("ix_rent_tenant_user", Rent.tenant_id, Rent.user_id)
