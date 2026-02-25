import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import select

from bot_strings.enum_str import PRODUCT_TYPE_LABEL
from bot_strings.rent_command_strings import RentStrings
from database.products.available_product import get_available_products
from database.session import async_session_maker, get_user_language
from keyboards.common_keyboards import build_select_keyboard, build_taxta_keyboard, build_metal_keyboard
from states import RentStatus
from utils.current_user import get_current_user
from utils.enums import ProductTypeEnum

router = Router(name=__name__)


@router.message(RentStatus.product_choice)
async def handle_selected_product(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    selected_label = (message.text or "").strip()

    # 1) current user + tenant
    current_user = await get_current_user(message)
    if not current_user:
        await message.answer(
            {"uzl": "Avval ro‘yxatdan o‘ting: /start",
             "uzk": "Аввал рўйхатдан ўтинг: /start",
             "rus": "Сначала зарегистрируйтесь: /start"}.get(lang, "Аввал ro‘yxatdan o‘ting: /start")
        )
        return

    await state.update_data(user_id=current_user.id)

    # 2) tenant bo'yicha available product types
    async with async_session_maker() as session:
        available_products = await get_available_products(session, tenant_id=current_user.tenant_id)

    available_types = {p.product_type for p, _remaining in available_products}  # set[ProductTypeEnum]
    allowed_labels = [PRODUCT_TYPE_LABEL[lang][t.value] for t in available_types]  # label list

    # 3) User noto'g'ri matn yozsa — qayta keyboard
    if selected_label not in allowed_labels:
        await message.answer(
            text={"uzl": "Iltimos, faqat quyidagi tugmalardan tanlang.",
                  "uzk": "Илтимос, фақат қуйидаги тугмалардан танланг.",
                  "rus": "Пожалуйста, выберите только одну из кнопок ниже."}.get(lang, "Илтимос, фақат қуйidagi тугмаларdan tanlang."),
            reply_markup=build_select_keyboard(allowed_labels),
        )
        return

    # 4) label -> enum mapping (LANG ichidagi labelni enumga aylantiramiz)
    label_to_enum = {label: enum_value for enum_value, label in PRODUCT_TYPE_LABEL[lang].items()}
    # enum_value bu sizning mappingda string bo'lishi mumkin (masalan "taxta_opalubka")
    product_type_value = label_to_enum[selected_label]  # masalan: "taxta_opalubka"

    # ProductTypeEnum ga aylantirib olamiz (xatoni oldini oladi)
    product_type_enum = ProductTypeEnum(product_type_value)

    data = await state.get_data()
    rent_info = data.get("rent_info", [])
    rent_info.append({"product_type": product_type_enum.value})
    await state.update_data(rent_info=rent_info)

    # 5) Keyingi state
    if product_type_enum == ProductTypeEnum.taxta_opalubka:
        await state.set_state(RentStatus.taxta_size_choice)
        size_text = {
            "uzl": "Iltimos, taxta opalubka uchun o'lcham tanlang:",
            "uzk": "Илтимос, тахта опалубка учун ўлчам танланг:",
            "rus": "Выберите размер для дощатой опалубки:",
        }.get(lang, "Илтимос, тахта опалубка учун ўлчам танланг:")
        await message.answer(text=size_text, reply_markup=build_taxta_keyboard(lang))
        return

    if product_type_enum == ProductTypeEnum.metal_opalubka:
        await state.set_state(RentStatus.metal_size_choice)
        size_text = {
            "uzl": "Iltimos, metal opalubka uchun o'lcham tanlang:",
            "uzk": "Илтимос, метал опалубка учун ўлчам танланг:",
            "rus": "Выберите размер для металлической опалубки:",
        }.get(lang, "Илтимос, метал опалубка учун ўлчам танланг:")
        await message.answer(text=size_text, reply_markup=build_metal_keyboard(lang))
        return

    # Monolit / Lesa (siz hozir lesa size ishlatmayapsiz) -> quantity
    await state.set_state(RentStatus.quantity)
    await message.answer(
        text=RentStrings.INSERT_QUANTITY_PRODUCT[lang],
        reply_markup=ReplyKeyboardRemove()
    )