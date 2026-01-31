from database.products.available_product import get_available_products
from utils.get_user_from_db import get_user_by_telegram_or_phone
from bot_strings.rent_command_strings import RentStrings
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils.enums import LanguageEnum, ProductTypeEnum, ProductSizeEnum
from database.session import async_session_maker
from aiogram import types



# async def build_products_reply_keyboard(message: types.Message):
#     telegram_id = message.from_user.id
#     async with async_session_maker() as session:
#         available_products = await get_available_products(session)
#         user = await get_user_by_telegram_or_phone(
#             db=session,
#             telegram_id=telegram_id,
#         )
#         lang = user.selected_language if user else LanguageEnum.uzk.name
#
#         builder = ReplyKeyboardBuilder()
#         for product in available_products:
#             # Mahsulot nomini keyboard uchun olingan tilga tarjima qilamiz
#             if product.product_type.name == ProductTypeEnum.lesa.name:
#                 # Lesa turini va o'lchamini ajratamiz
#                 size_name = product.product_size.name
#                 text = RentStrings.CHOOSE_PRODUCT_KEYBOARD[lang][ProductTypeEnum.lesa.name][size_name]
#             else:
#                 # Monolit va Taxta
#                 text = RentStrings.CHOOSE_PRODUCT_KEYBOARD[lang][product.product_type.name]
#
#             # Agar kerak bo'lsa qoldiqni qo‘shamiz
#             # if lang == "uzl":
#             #     text += f" - Qoldiq:  {product.total_quantity}"
#             # elif lang == "uzk":
#             #     text += f" - Қолдиқ:  {product.total_quantity}"
#             # elif lang == "rus":
#             #     text += f" - Остальные:  {product.total_quantity}"
#
#             builder.button(text=text)
#
#         builder.adjust(1)  # Har bir tugma alohida qatorda
#         return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

# def select_product_size():
#