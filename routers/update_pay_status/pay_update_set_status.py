from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import select

from database.session import async_session_maker, get_user_language
from db.models import Rent
from utils.enums import PaymentStatusEnum

router = Router(name=__name__)

@router.callback_query(F.data.startswith("payupd_set:"))
async def pay_update_set_status(call: CallbackQuery, state: FSMContext):
    lang = await get_user_language(call)

    _, rent_id_str, status_str = call.data.split(":")
    rent_id = int(rent_id_str)

    mapping = {
        "full_paid": PaymentStatusEnum.full_paid,
        "part_paid": PaymentStatusEnum.part_paid,
        "not_paid": PaymentStatusEnum.not_paid,
    }
    new_status = mapping.get(status_str)
    if not new_status:
        await call.answer("❌ Хатолик!")
        return

    async with async_session_maker() as session:
        rent = (await session.execute(
            select(Rent).where(Rent.id == rent_id)
        )).scalar_one_or_none()

        if not rent:
            await call.message.answer(
                {
                    "uzl": "Ijara topilmadi.",
                    "uzk": "Ижара топилмади.",
                    "rus": "Прокат не найден..",
                }
            )
            await call.answer()
            return

        rent.status = new_status
        await session.commit()

    await call.message.edit_text(
        {
            "uzl": f"✅ To‘lov holati yangilandi: {new_status.value} (ijara #{rent_id})",
            "uzk": f"✅ Тўлов ҳолати янгиланди: {new_status.value} (ижара #{rent_id})",
            "rus": f"✅ Статус оплаты обновлён: {new_status.value} (аренда #{rent_id})",
        }[lang]
    )
    await state.clear()
    await call.answer()