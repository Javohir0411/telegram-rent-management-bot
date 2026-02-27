from aiogram import Router
from .handle_inserted_name import router as handle_inserted_name_router

router = Router(name=__name__)

router.include_routers(
    handle_inserted_name_router,
)