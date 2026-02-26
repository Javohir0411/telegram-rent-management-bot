import asyncio
from database.session import async_session_maker
from db.models import Product
from utils.enums import ProductTypeEnum, ProductSizeEnum


TENANT_ID = 38  # qaysi tenant uchun product qo'shyapsan


async def add_products():
    async with async_session_maker() as session:
        products = [
            Product(
                tenant_id=TENANT_ID,
                product_type=ProductTypeEnum.lesa,
                total_quantity=273,
                price_per_day=3000
            ),
            Product(
                tenant_id=TENANT_ID,
                product_type=ProductTypeEnum.monolit,
                product_size=None,
                total_quantity=20,
                price_per_day=5000
            ),
            Product(
                tenant_id=TENANT_ID,
                product_type=ProductTypeEnum.taxta_opalubka,
                product_size=ProductSizeEnum.four_meters,
                total_quantity=30,
                price_per_day=2500
            ),
            Product(
                tenant_id=TENANT_ID,
                product_type=ProductTypeEnum.taxta_opalubka,
                product_size=ProductSizeEnum.three_meters,
                total_quantity=30,
                price_per_day=2000
            ),
            Product(
                tenant_id=TENANT_ID,
                product_type=ProductTypeEnum.taxta_opalubka,
                product_size=ProductSizeEnum.two_meters,
                total_quantity=10,
                price_per_day=1500
            ),
            Product(
                tenant_id=TENANT_ID,
                product_type=ProductTypeEnum.taxta_opalubka,
                product_size=ProductSizeEnum.one_meter,
                total_quantity=10,
                price_per_day=1200
            ),
            Product(
                tenant_id=TENANT_ID,
                product_type=ProductTypeEnum.metal_opalubka,
                product_size=ProductSizeEnum.three_meters,
                total_quantity=10,
                price_per_day=1500
            ),
        ]

        session.add_all(products)
        await session.commit()
        print("Barcha product-lar bazaga qo'shildi!")


if __name__ == "__main__":
    asyncio.run(add_products())