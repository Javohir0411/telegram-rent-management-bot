from .start import router as start_router
from .help import router as help_router
from .rent import router as rent_router
from .leased import router as leased_router
from .total import router as total_router
from .return_rent import router as return_rent_router
from .bot_settings import router as bot_settings_router
from .rent_report import router as rent_report_router
from .pay_update import router as pay_update_router
from .add_product import router as add_product_router
from aiogram import Router

router = Router(name=__name__)

router.include_routers(
    start_router,
    help_router,
    rent_router,
    leased_router,
    total_router,
    return_rent_router,
    bot_settings_router,
    rent_report_router,
    pay_update_router,
    add_product_router,
)
