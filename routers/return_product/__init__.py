from aiogram import Router
from .choose_renter import router as choose_renter_router
from .choose_product import router as choose_product_router
from .enter_quantity import router as enter_quantity_router
from .enter_end_date import router as enter_end_date_router

router = Router(name=__name__)

router.include_routers(
    choose_renter_router,
    choose_product_router,
    enter_quantity_router,
    enter_end_date_router,
)
