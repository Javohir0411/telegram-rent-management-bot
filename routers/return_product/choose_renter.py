# choose_renter.py
import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot_strings.enum_str import PRODUCT_TYPE_LABEL
from database.session import get_user_language, async_session_maker
from db.models import Renter, Rent
from keyboards.common_keyboards import build_select_keyboard
from states import ReturnProduct
from utils.enums import RentStatusEnum
from utils.current_user import get_current_user

router = Router(name=__name__)


@router.message(F.text, ReturnProduct.choosing_renter)
async def handle_choosing_renter(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)

    try:
        renter_id = int(message.text.split("(#")[-1].replace(")", "").strip())
    except Exception:
        await message.answer("Iltimos ro‘yxatdan tugma orqali tanlang.")
        return

    current_user = await get_current_user(message)
    if not current_user:
        await message.answer(
            {"uzl": "Avval /start qiling", "uzk": "Аввал /start қилинг", "rus": "Сначала /start"}[lang])
        return

    tenant_id = current_user.tenant_id

    async with async_session_maker() as session:
        # renter mavjudligini tekshiramiz
        renter = await session.scalar(
            select(Renter)
            .where(Renter.id == renter_id, Renter.tenant_id == tenant_id)
        )

        if not renter:
            await message.answer(
                {"uzl": "Bunday ijarachi topilmadi", "uzk": "Бундай ижарачи топилмади", "rus": "Арендатор не найден"}[
                    lang]
            )
            return

        # faqat active rentlarni DBdan olamiz (eng to‘g‘ri yo‘l)
        result = await session.execute(
            select(Rent)
            .options(selectinload(Rent.product))
            .where(
                Rent.renter_id == renter_id,
                Rent.tenant_id == tenant_id,
                Rent.rent_status == RentStatusEnum.active
            )
            .order_by(Rent.id.desc())
        )

        active_rents = result.scalars().all()

        if not active_rents:
            await message.answer(
                {"uzl": "Bu ijarachida faol ijara yo‘q", "uzk": "Фаол ижара йўқ", "rus": "Нет активной аренды"}[lang]
            )
            return

        items = []
        for r in active_rents:
            p = r.product
            items.append(f"{PRODUCT_TYPE_LABEL[lang][p.product_type.value]} ({r.quantity}) - (id:{r.id})")

        kb = build_select_keyboard(items)
        await state.update_data(renter_id=renter.id)
        await state.set_state(ReturnProduct.choosing_product)
        await message.answer(
            {"uzl": "Qaytariladigan mahsulotni tanlang: ",
             "uzk": "Қайтариладиган маҳсулотни танланг: ",
             "rus": "Выберите товар для возврата: "}[lang],
            reply_markup=kb
        )
