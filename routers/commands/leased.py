# leased_handler.py
import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyexpat.errors import messages

from bot_strings.enum_str import PRODUCT_TYPE_LABEL, SIZE_LABEL
from bot_strings.leased_command_strings import Leased
from database.session import get_user_language
from utils.admin_only import AdminOnly
from utils.enums import RentStatusEnum
from utils.get_leased_rent import get_leased_rents

router = Router(name=__name__)

# Rent status label mapping
RENT_STATUS_LABEL = {
    RentStatusEnum.active: "Ижарада",
    RentStatusEnum.returned: "Қайтарилган"
}

# Pagination
RENT_PER_PAGE = 3  # har sahifada nechta rent ko‘rsatiladi


def build_pagination_keyboard(total_items: int, current_page: int) -> InlineKeyboardMarkup | None:
    total_pages = (total_items + RENT_PER_PAGE - 1) // RENT_PER_PAGE
    buttons = []

    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"leased_page:{current_page - 1}")
        )
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"leased_page:{current_page + 1}")
        )

    if not buttons:
        return None

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def format_rent_text(rents_slice, lang: str) -> str:
    text = ""
    for i, rent in enumerate(rents_slice, start=1):
        product = rent.product
        renter = rent.renter

        status_label = RENT_STATUS_LABEL[rent.rent_status]

        start_date = rent.start_date.strftime("%d-%m-%Y") if rent.start_date else ""
        end_date = rent.end_date.strftime("%d-%m-%Y") if rent.end_date else " — "

        rent_text = Leased.RESULT[lang].format(
            rent=rent,
            renter=renter,
            status_label=status_label,
            start_date=start_date,
            end_date=end_date
        )

        product_name = PRODUCT_TYPE_LABEL[lang][product.product_type]  # enum bilan ishlating
        size_text = f" ({SIZE_LABEL[lang][product.product_size]})" if product and product.product_size else ""

        text += f"<b>{i}) {product_name}{size_text}</b>{rent_text}"
    return text


@router.message(Command("leased", prefix="/!"))
async def handle_leased_command(message: types.Message):
    rents = await get_leased_rents(message)
    lang = await get_user_language(message)

    if not rents:
        await message.answer(Leased.NOT_PRODUCT_IN_RENT[lang])
        logging.info(f"LEASED COMMAND BERGAN AMMO IJARASI YOQ TELEGRAM ID: {message.from_user.id}")
        return

    # Header
    header = {
        "uzl": "📦 Ijaraga berilgan mahsulotlar:\n\n",
        "uzk": "📦 Ижарага берилган маҳсулотлар:\n\n",
        "rus": "📦 Продукты в аренду:\n\n"
    }.get(lang, "📦 Ijaraga berilgan mahsulotlar:\n\n")

    # Birinchi sahifa
    page = 1
    start_idx = (page - 1) * RENT_PER_PAGE
    end_idx = start_idx + RENT_PER_PAGE
    rents_slice = rents[start_idx:end_idx]

    text = header + format_rent_text(rents_slice, lang)
    kb = build_pagination_keyboard(total_items=len(rents), current_page=page)

    tenant_ids = {r.tenant_id for r in rents}
    logging.info(f"IJARAGA BERGAN ID VA TENANT ID: {tenant_ids} | {message.from_user.id}")
    await message.answer(text=text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith("leased_page:"))
async def handle_leased_pagination(callback: CallbackQuery):
    rents = await get_leased_rents(callback)
    lang = await get_user_language(callback)
    logging.info(f"LEASED PAGINATION: {lang}")

    page = int(callback.data.split(":")[1])
    start_idx = (page - 1) * RENT_PER_PAGE
    end_idx = start_idx + RENT_PER_PAGE
    rents_slice = rents[start_idx:end_idx]

    header = {
        "uzl": "📦 Ijaraga berilgan mahsulotlar:\n\n",
        "uzk": "📦 Ижарага берилган маҳсулотлар:\n\n",
        "rus": "📦 Продукты в аренду:\n\n"
    }.get(lang, "📦 Ижарага берилган маҳсулотлар:\n\n")

    text = header + format_rent_text(rents_slice, lang)
    kb = build_pagination_keyboard(total_items=len(rents), current_page=page)

    await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()
