from database.session import get_user_language, async_session_maker
from bot_strings.enum_str import PRODUCT_TYPE_LABEL, PAYMENT_STATUS, RENT_STATUS
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import selectinload
from aiogram import Router, F
from sqlalchemy import select
from db.models import Rent
import logging
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from states import PayUpdateState
from utils.current_user import get_current_user

router = Router(name=__name__)


@router.callback_query(F.data.startswith("payupd_renter:"))
async def handle_payupd_renter(call: CallbackQuery, state: FSMContext):
    lang = await get_user_language(call)
    current_user = await get_current_user(call)

    logging.info(f"HANDLE PAYUPD RENTER CALLBACK: {call.data}")
    logging.info(f"PAY UPDATE GA KIRGAN USER: {call.message.from_user.id}")
    renter_id = int(call.data.split(":")[1])
    await state.update_data(pay_update_renter_id=renter_id)
    logging.info(f"PAYMENT UPDATE RENTER ID: {renter_id}")

    async with async_session_maker() as session:
        stmt = (
            select(Rent)
            .where(
                Rent.tenant_id == current_user.tenant_id,
                Rent.renter_id == renter_id)  # ✅ to'g'ri
            .options(selectinload(Rent.product), selectinload(Rent.renter))
            .order_by(Rent.id.desc())
            .limit(20)
        )
        result = await session.execute(stmt)
        rents = result.scalars().all()
        logging.info(f"RENTS IN PAYUPD RENTER: {rents}")

        if not rents:
            await call.message.answer(
                text={
                    "uzl": "❌ Bu ijarachida ijara topilmadi.",
                    "uzk": "❌ Бу ижарачида ижара топилмади..",
                    "rus": "❌ Информация об арендной плате для этого арендатора не найдена.",
                }.get(lang, "Бу ижарачида ижара топилмади.")
            )
            return
        rows = []
        for r in rents:
            product_label = f"{PRODUCT_TYPE_LABEL[lang][r.product.product_type.value]}" if r.product else f"product_id = {r.product_id}"
            start_date = r.start_date.strftime("%d.%m.%Y") if r.start_date else "-"
            end_date = r.end_date.strftime("%d.%m.%Y") if r.end_date else "-"
            payment_status = r.status.name if r.status else "-"
            rent_status = r.rent_status.name if r.rent_status else "-"
            rows.append((r.id, product_label, start_date, end_date, payment_status, rent_status))
            logging.info(f"HANDLE PAYMENT RENTER ROWS: {rows}")

        text_lines = ["Quyidagi ijaralardan birini tanlang (oxirgi 20 ta):\n"]
        for rid, prod, sd, ed, pay, rentst in rows:
            text_lines.append(f"🆔 Ижара ID рақами: #{rid}\n\n"
                              f"🛒 Маҳсулот номи: {prod}\n\n"
                              f"🗓️ Ижарани бошланиш ва тугаш санаси: {sd} → {ed}\n\n"
                              f"💳 Тўлов ҳолати: {PAYMENT_STATUS[lang][pay]}\n\n"
                              f"📊 Ижара ҳолати: {RENT_STATUS[lang][rentst]}\n\n"
                              # f"-ˋˏ✄- - - - - - - - - - - - - \n"
                              f"⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘\n\n")
            logging.info(f"TEXT LINES: {text_lines}")

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"#{r.id} — {PRODUCT_TYPE_LABEL[lang][r.product.product_type.value] if r.product else r.product_id}",
                    callback_data=f"payupd_rent:{r.id}"
                )]
                for r in rents
            ]
        )

        await call.message.edit_text("\n".join(text_lines))
        await call.message.answer(
            {
                "uzl": "Qaysi ijarani yangilaymiz?",
                "uzk": "Қайси ижарани янгилаймиз?",
                "rus": "Какую аренду обновляем?",
            }[lang],
            reply_markup=kb
        )
        await call.answer()
