import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import async_session_maker
from db.models import Product, Rent
from utils.enums import RentStatusEnum

logging.basicConfig(level=logging.INFO)


# async def get_available_products(session):
#     q = (
#         select(
#             Product,
#             func.coalesce(func.sum(Rent.quantity), 0).label("rented_qty"),
#         )
#         .outerjoin(
#             Rent,
#             (Rent.product_id == Product.id) &
#             (Rent.rent_status == RentStatusEnum.active)
#         )
#         .group_by(Product.id)
#     )
#
#     rows = (await session.execute(q)).all()
#
#     available_products = []
#     for product, rented_qty in rows:
#         remaining = product.total_quantity - rented_qty
#         if remaining > 0:
#             available_products.append((product, remaining))
#
#     return available_products

from sqlalchemy import func, select
from db.models import Product, Rent
from utils.enums import RentStatusEnum

async def get_available_products(session):
    rented_qty_expr = func.coalesce(
        func.sum(Rent.quantity - func.coalesce(Rent.returned_quantity, 0)),
        0
    )

    q = (
        select(Product, rented_qty_expr.label("rented_qty"))
        .outerjoin(
            Rent,
            (Rent.product_id == Product.id) &
            (Rent.rent_status == RentStatusEnum.active)   # enum value "active" bo‘lishi shart
        )
        .group_by(Product.id)
    )

    rows = (await session.execute(q)).all()

    available_products = []
    for product, rented_qty in rows:
        remaining = product.total_quantity - rented_qty
        if remaining > 0:
            available_products.append((product, remaining))

    return available_products

