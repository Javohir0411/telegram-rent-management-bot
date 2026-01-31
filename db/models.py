from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    DateTime,
    func,
    ForeignKey,
    Date,
    Enum, Text, Float, Boolean, UniqueConstraint,

)
from sqlalchemy.orm import relationship

from database.base import Base
from utils.enums import RentStatusEnum, ProductTypeEnum, PaymentStatusEnum, ProductSizeEnum


#
#
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    user_fullname = Column(String, nullable=False)
    user_phone_number = Column(String, unique=True, nullable=False)
    selected_language = Column(String, nullable=False)
    rents = relationship("Rent", back_populates="user")
    created_at = Column(Date, server_default=func.current_date())  # Avtomatik kiritish vaqtini saqlash
    updated_at = Column(Date, server_default=func.current_date(),
                        onupdate=func.now())  # Yangilangan vaqtini avtomatik saqlash


class Renter(Base):
    __tablename__ = "renter"

    id = Column(Integer, primary_key=True, index=True)
    renter_fullname = Column(String, nullable=False)
    renter_phone_number = Column(String, unique=False, nullable=False)
    renter_passport_info = Column(String, nullable=True)

    rents = relationship("Rent", back_populates="renter")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    product_type = Column(Enum(ProductTypeEnum, name="product_type_enum"), nullable=False)
    product_size = Column(Enum(ProductSizeEnum, name="product_size_enum"), nullable=True)
    total_quantity = Column(Integer, nullable=False)
    price_per_day = Column(Float, nullable=True)

    rents = relationship("Rent", back_populates="product")


class Rent(Base):
    __tablename__ = "rents"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # yangi field
    renter_id = Column(Integer, ForeignKey("renter.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    delivery_needed = Column(Boolean, nullable=True, default=False)
    delivery_price = Column(Float, nullable=True)
    product_price = Column(Float, nullable=True)
    rent_price = Column(Float, nullable=True)
    comment = Column(Text, nullable=False)
    status = Column(Enum(PaymentStatusEnum), nullable=False)
    rent_status = Column(Enum(RentStatusEnum), nullable=False)

    user = relationship("User", back_populates="rents")  # yangi relationship
    renter = relationship("Renter", back_populates="rents")
    product = relationship("Product", back_populates="rents")

    created_at = Column(Date, server_default=func.current_date())  # Avtomatik kiritish vaqtini saqlash
    updated_at = Column(Date, server_default=func.current_date(),
                        onupdate=func.now())  # Yangilangan vaqtini avtomatik saqlash
