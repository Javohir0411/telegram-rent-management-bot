from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Product
from utils.enums import ProductTypeEnum, ProductSizeEnum


async def create_or_update_product(
        session: AsyncSession,
        *,
        tenant_id: int,
        product_type: ProductTypeEnum,
        product_size: Optional[ProductSizeEnum],
        add_quantity: int,
        price_per_day: float,
) -> Product:
    if add_quantity <= 0:
        raise ValueError("add_quantity must be > 0")
    if price_per_day <= 0:
        raise ValueError("price_per_day must be > 0")

    stmt = (
        select(Product)
        .where(
            Product.tenant_id == tenant_id,
            Product.product_type == product_type,
            Product.product_size.is_(None) if product_size is None else Product.product_size == product_size,
        )
        .limit(1)
    )
    res = await session.execute(stmt)
    product = res.scalar_one_or_none()

    if product:
        product.total_quantity += add_quantity
        product.price_per_day = float(price_per_day)
    else:
        product = Product(
            tenant_id=tenant_id,
            product_type=product_type,
            product_size=product_size,  # None bo'lishi mumkin (lesa/monolit)
            total_quantity=add_quantity,
            price_per_day=float(price_per_day),
        )
        session.add(product)

    await session.commit()
    await session.refresh(product)
    return product
