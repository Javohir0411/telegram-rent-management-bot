import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot_strings.enum_str import PRODUCT_TYPE_LABEL, SIZE_LABEL
from database.session import get_user_language, async_session_maker
from db.models import Rent, Product
from states import ReturnProduct
from utils.enums import RentStatusEnum

logging.basicConfig(level=logging.INFO)
router = Router(name=__name__)


@router.message(ReturnProduct.choosing_product)
async def product_selected(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    product_text = message.text  # misol: "Lesa | katta (10)"
    logging.info(f"PRODUCT TEXT: {product_text}")
    product_text_wo_q = product_text.split("(")[0].strip()
    logging.info(f"PRODUCT TEXT WO Q: {product_text_wo_q}")
    data = await state.get_data()
    renter_id = data["renter_id"]

    async with async_session_maker() as session:
        result = await session.execute(
            select(Rent)
            .options(selectinload(Rent.product))  # Product-ni oldindan yuklaymiz
            .where(Rent.renter_id == renter_id)
            .where(Rent.rent_status == RentStatusEnum.active)
        )
        active_rents = result.scalars().all()

        # Tanlangan mahsulotni aniqlash
        rent = None
        for r in active_rents:
            logging.info(f"R.ID: {r.id}")
            size = f" | {SIZE_LABEL[lang][r.product.product_size]}" if r.product.product_size else ""
            key_text = f"{PRODUCT_TYPE_LABEL[lang][r.product.product_type]}{size} ({r.quantity})"
            logging.info(f"KEY TEXT: {key_text}")
            logging.info(f"R PRODUCT TYPE: {r.product.product_type}")
            if PRODUCT_TYPE_LABEL[lang][r.product.product_type] == product_text_wo_q:
                logging.info(
                    f"PRODUCT_TYPE_LABEL[lang][r.product.product_type]: {PRODUCT_TYPE_LABEL[lang][r.product.product_type.value]}")
                rent = r
                break

        if not rent:
            await message.answer("Маҳсулот топилмади, қайта уриниб кўринг.")
            logging.info("Маҳсулот топилмади, қайта уриниб кўринг.")
            logging.info(
                f"PRODUCT_TYPE_LABEL[lang][r.product.product_type]: {PRODUCT_TYPE_LABEL[lang][r.product.product_type]}")
            return

        await state.update_data(rent_id=rent.id)
        await message.answer(
            {
                "uzl": f"Qancha mahsulot qaytarildi? (max {rent.quantity})",
                "uzk": f"Қанча маҳсулот қайтарилди? (max {rent.quantity})",
                "rus": f"Сколько товаров было возвращено? (max {rent.quantity})",
            }[lang],
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(ReturnProduct.entering_quantity)
