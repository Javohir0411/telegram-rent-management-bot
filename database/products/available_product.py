import logging
from sqlalchemy import func, select
from db.models import Product, Rent
from utils.enums import RentStatusEnum

logging.basicConfig(level=logging.INFO)


async def get_available_products(session, tenant_id: int):
    # Rent hisobida ham tenant bo'lishi shart
    rented_qty_expr = func.coalesce(
        func.sum(Rent.quantity - func.coalesce(Rent.returned_quantity, 0)),
        0
    )

    q = (
        select(Product, rented_qty_expr.label("rented_qty"))
        .where(Product.tenant_id == tenant_id)  # ✅ faqat shu tenant productlari
        .outerjoin(
            Rent,
            (Rent.product_id == Product.id)
            & (Rent.rent_status == RentStatusEnum.active)
            & (Rent.tenant_id == tenant_id)     # ✅ faqat shu tenant rentlari
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