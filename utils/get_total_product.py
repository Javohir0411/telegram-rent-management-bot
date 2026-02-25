from sqlalchemy import func, select

from database.session import async_session_maker
from db.models import Product


async def get_total_product(tenant_id: int):
    async with async_session_maker() as session:
        result = await session.execute(
            select(
                Product.product_type,
                Product.product_size,
                func.sum(Product.total_quantity).label("total_qty"),
            )
            .where(Product.tenant_id == tenant_id)   # ✅ FILTER
            .group_by(Product.product_type, Product.product_size)
            .order_by(Product.product_type.asc())
        )
        return result.all()