from utils.current_user import get_current_user
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from database.session import (
    async_session_maker,
    get_user_language
)
from sqlalchemy import select
from db.models import Tenant
from states import Register

router = Router(name=__name__)


@router.message(F.location, Register.warehouse_location)
async def handle_warehouse_location(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    user = await get_current_user(message)

    lat = message.location.latitude
    lon = message.location.longitude

    async with async_session_maker() as session:
        tenant = (await session.execute(
            select(Tenant).where(Tenant.id == user.tenant_id)
        )).scalar_one()

        tenant.base_latitude = lat
        tenant.base_longitude = lon
        await session.commit()

    await message.answer(
        {
            "uzl": "✅ Ombor lokatsiyasi saqlandi.",
            "uzk": "✅ Омбор локацияси сақланди.",
            "rus": "✅ Местоположение склада сохранено.",
        }.get(lang, "✅ Омбор локацияси сақланди.")
    )
    await state.clear()


@router.message(Register.warehouse_location)
async def handle_invalid(message: types.Message):
    lang = await get_user_language(message)
    await message.reply(
        {
            "uzl": "Iltimos, joylashuvni yuboring!\n"
                   "Joylashuvdan boshqa hech qanday xabar qabul qilinmaydi.",

            "uzk": "Илтимос, жойлашувни юборинг!\n"
                   "Жойлашувдан бошқа ҳеч қандай хабар қабул қилинмайди.",

            "rus": "Пожалуйста, пришлите местоположение!\n"
                   "Сообщения, содержащие только информацию о местоположении, не принимаются."
        }.get(lang, "Илтимос, жойлашувни юборинг!\n"
                    "Жойлашувдан бошқа ҳеч қандай хабар қабул қилинмайди."
              ),
        reply_markup=types.ReplyKeyboardRemove(),
    )
