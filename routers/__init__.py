__all__ = ("router",)

from aiogram import Router
from .commands import router as command_router
from .register_user_handlers import router as register_user_router
from .product_rental import router as product_rental_router
from .rent_process import router as renter_router
from .return_product import router as return_product_router
from .setting_callback import router as settings_callback_router
from .services import router as service_router
from .update_pay_status import router as update_pay_status_router

router = Router(name=__name__)

router.include_routers(
    command_router,
    register_user_router,
    product_rental_router,
    renter_router,
    return_product_router,
    settings_callback_router,
    service_router,
    update_pay_status_router,
)
