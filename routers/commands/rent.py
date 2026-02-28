from database.products.available_product import get_available_products  # buni ham tenantli qilamiz
from keyboards.common_keyboards import build_select_keyboard
from bot_strings.rent_command_strings import RentStrings
from bot_strings.enum_str import PRODUCT_TYPE_LABEL
from utils.current_user import get_current_user
from aiogram.fsm.context import FSMContext
from utils.enums import ProductTypeEnum
from aiogram import Router, types, F
from aiogram.filters import Command
import logging
from database.session import (
    get_user_language,
    async_session_maker
)
from states import RentStatus

logging.basicConfig(level=logging.INFO)
router = Router(name=__name__)


@router.message(Command("rent", prefix="/!"))
async def handle_command_rent(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)

    current_user = await get_current_user(message)
    if not current_user:
        await message.answer(
            {"uzl": "Avval ro‘yxatdan o‘ting: /start",
             "uzk": "Аввал рўйхатдан ўтинг: /start",
             "rus": "Сначала зарегистрируйтесь: /start"}.get(lang, "Аввал рўйхатдан ўтинг: /start")
        )
        return

    # user_id ni state ga yozib qo'yamiz (kim create qilganini korish uchun)
    await state.update_data(user_id=current_user.id, tenant_id=current_user.tenant_id)

    async with async_session_maker() as db:
        available_products = await get_available_products(db, tenant_id=current_user.tenant_id)

    if not available_products:
        await message.answer(
            {"uzl": "Hozircha mahsulotlar yo‘q.",
             "uzk": "Ҳозирча маҳсулотлар йўқ.",
             "rus": "Пока нет продуктов."}.get(lang, "Ҳозирча маҳсулотлар йўқ.")
        )
        return

    message_text = RentStrings.RENT_STARTING_PROCESS[lang]
    available_types: set[str] = set()

    for product, remaining_quantity in available_products:
        # display name
        if product.product_type.name == ProductTypeEnum.taxta_opalubka.name and product.product_size:
            size_name = product.product_size.name
            product_name = RentStrings.CHOOSE_PRODUCT_KEYBOARD[lang][ProductTypeEnum.taxta_opalubka.name][size_name]
        else:
            product_name = RentStrings.CHOOSE_PRODUCT_KEYBOARD[lang][product.product_type.name]

        available_types.add(product.product_type.name)
        print(f"AVAILABLE TYPES: {available_types}")

        # remaining qty
        if lang == "uzl":
            message_text += f"<b>{product_name}</b> - Qoldiq: <u>{remaining_quantity}</u>\n"
        elif lang == "uzk":
            message_text += f"<b>{product_name}</b> - Қолдиқ: <u>{remaining_quantity}</u>\n"
        else:  # rus
            message_text += f"<b>{product_name}</b> - Остаток: <u>{remaining_quantity}</u>\n"

    await state.set_state(RentStatus.product_choice)

    kb_labels = [PRODUCT_TYPE_LABEL[lang][t] for t in available_types]
    await message.answer(
        text=message_text,
        reply_markup=build_select_keyboard(kb_labels),
        parse_mode="HTML"
    )


@router.message(Command("cancel"), RentStatus())
@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel", RentStatus())
@router.message(F.text.casefold() == "cancel")
async def cancel_handle(message: types.Message, state: FSMContext) -> None:
    state_current = await state.get_state()
    if state_current is None:
        await message.answer(
            text="ОК, лекин ҳеч нарсани бошламаган эдик ҳали.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    await state.clear()
    await message.answer(
        text=f"Жараён <b><u>{state_current.split(':')[-1]}</u></b> қадамида тўхтатилди.",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
