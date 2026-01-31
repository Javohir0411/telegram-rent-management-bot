from aiogram import Router
from .handle_selected_product import router as selected_product_router
from .handle_selected_size import router as selected_lesa_size_router
from .handle_product_quantity import router as product_quantity_router
from .handle_yes_or_no import router as yes_or_no_router

router = Router(name=__name__)

router.include_routers(
    selected_product_router,
    selected_lesa_size_router,
    product_quantity_router,
    yes_or_no_router,
)
