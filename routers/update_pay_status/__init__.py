from aiogram import Router
from .pay_update_choose_renter import router as pay_update_choose_renter_router
from .pay_update_choose_rent import router as pay_update_choose_rent_router
from .pay_update_set_status import router as pay_update_set_status_router

router = Router()

router.include_routers(
    pay_update_choose_renter_router,
    pay_update_choose_rent_router,
    pay_update_set_status_router,
)
