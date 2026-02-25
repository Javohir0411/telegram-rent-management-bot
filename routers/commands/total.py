from aiogram import Router, types
from aiogram.filters import Command

from bot_strings.enum_str import PRODUCT_TYPE_LABEL, SIZE_LABEL
from database.session import get_user_language
from utils.admin_only import AdminOnly
from utils.current_user import get_current_user
from utils.get_total_product import get_total_product

router = Router(name=__name__)


@router.message(Command("total", prefix="/!"))
async def handle_total_command(message: types.Message):
    lang = await get_user_language(message)

    current_user = await get_current_user(message)
    if not current_user:
        await message.answer(
            {"uzl": "Avval /start qiling", "uzk": "Аввал /start қилинг", "rus": "Сначала /start"}[lang]
        )
        return

    totals = await get_total_product(tenant_id=current_user.tenant_id)  # ✅ tenant bo‘yicha

    if not totals:
        await message.answer(
            {
                "uzl": "Hozircha mahsulotlar mavjud emas.",
                "uzk": "Ҳозирча маҳсулотлар мавжуд эмас.",
                "rus": "Пока нет доступных товаров.",
            }.get(lang, "Hozircha mahsulotlar mavjud emas.")
        )
        return

    text = {
        "uzl": "📦 Umumiy mahsulotlar:\n\n",
        "uzk": "📦 Умумий маҳсулотлар:\n\n",
        "rus": "📦 Общие товары:\n\n",
    }.get(lang, "📦 Umumiy mahsulotlar:\n\n")

    for product_type, product_size, total_qty in totals:
        type_text = PRODUCT_TYPE_LABEL[lang][product_type]
        size_text = f" ({SIZE_LABEL[lang][product_size]})" if product_size else ""
        text += f"<b>{type_text}</b>{size_text}:  <u>{int(total_qty)}</u>\n"

    await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")
