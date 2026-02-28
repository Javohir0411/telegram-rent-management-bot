from database.products.available_product import get_available_products
from bot_strings.rent_command_strings import RentStrings
from bot_strings.enum_str import PRODUCT_TYPE_LABEL
from utils.current_user import get_current_user
from aiogram.fsm.context import FSMContext
from keyboards.common_keyboards import (
    build_select_keyboard,
    build_yes_or_no_kb
)
from utils.enums import ProductTypeEnum
from aiogram import Router, types, F
from states import RentStatus
from database.session import (
    async_session_maker,
    get_user_language
)
import logging

logging.basicConfig(level=logging.INFO)
router = Router(name=__name__)


@router.message(RentStatus.additional_choice, F.text.casefold() == "yes")
async def handle_additional_choice_ok(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)

    current_user = await get_current_user(message)
    if not current_user:
        await message.answer(
            {"uzl": "Avval ro‘yxatdan o‘ting: /start",
             "uzk": "Аввал рўйхатдан ўтинг: /start",
             "rus": "Сначала зарегистрируйтесь: /start"}.get(lang, "Аввал ro‘yxatdan o‘ting: /start")
        )
        return

    async with async_session_maker() as session:
        available_products = await get_available_products(session, tenant_id=current_user.tenant_id)

    await state.update_data(additional_choice=True)
    await state.set_state(RentStatus.product_choice)

    text = RentStrings.CHOOSE_ANOTHER_PRODUCT[lang]
    available_types: set[str] = set()

    for product, remaining_quantity in available_products:
        if product.product_type.name == ProductTypeEnum.taxta_opalubka.name and product.product_size:
            size_name = product.product_size.name
            product_name = RentStrings.CHOOSE_PRODUCT_KEYBOARD[lang][ProductTypeEnum.taxta_opalubka.name][size_name]
        else:
            product_name = RentStrings.CHOOSE_PRODUCT_KEYBOARD[lang][product.product_type.name]

        available_types.add(product.product_type.value)  # ✅ value bilan bir xil yuritamiz

        if lang == "uzl":
            text += f"<b>{product_name}</b> - Qoldiq: {remaining_quantity}\n"
        elif lang == "uzk":
            text += f"{product_name} - Қолдиқ: {remaining_quantity}\n"
        else:  # rus
            text += f"{product_name} - Остаток: {remaining_quantity}\n"

    kb = [PRODUCT_TYPE_LABEL[lang][t] for t in available_types]
    await message.answer(text=text, reply_markup=build_select_keyboard(kb), parse_mode="HTML")


@router.message(RentStatus.additional_choice, F.text.casefold() == "no")
async def handle_additional_choice_not_ok(message: types.Message, state: FSMContext):
    await state.update_data(additional_choice=False)
    lang = await get_user_language(message)

    await state.set_state(RentStatus.renter_fullname)
    await message.answer(
        text=RentStrings.ASK_RENTER_FULLNAME[lang],
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(RentStatus.additional_choice)
async def handle_additional_choice_could_not_understand(message: types.Message):
    lang = await get_user_language(message)
    await message.answer(
        text=RentStrings.INVALID_YES_NO[lang],
        reply_markup=build_yes_or_no_kb(),
    )
