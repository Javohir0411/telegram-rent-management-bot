from aiogram import Router
from .handle_inserted_name import router as handle_inserted_name_router
from .handle_name_yes_or_no import router as handle_name_yes_or_no_router
from .handle_inserted_product_quantity import router as handle_inserted_product_quantity_router
from .handle_inserted_size import router as handle_inserted_size_router
from .handle_inserted_price import router as handle_inserted_price_router

router = Router(name=__name__)

router.include_routers(
    handle_inserted_name_router,
    handle_name_yes_or_no_router,
    handle_inserted_product_quantity_router,
    handle_inserted_size_router,
    handle_inserted_price_router,
)