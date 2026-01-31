from database.products.available_product import get_available_products
from database.session import get_user_language, async_session_maker
from keyboards.common_keyboards import build_select_keyboard
from bot_strings.rent_command_strings import RentStrings
from bot_strings.enum_str import PRODUCT_TYPE_LABEL
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from utils.enums import ProductTypeEnum
from utils.admin_only import AdminOnly
from aiogram import Router, types, F
from aiogram.filters import Command
from states import RentStatus
from sqlalchemy import select
from database import session
from db.models import User
import logging

logging.basicConfig(level=logging.DEBUG)
router = Router(name=__name__)


@router.message(AdminOnly(), Command("rent", prefix="/!"))
async def handle_command_rent(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    logging.info(f"COMMAND RENT UCHUN KELGAN TIL: {lang}")

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        current_user = result.scalar_one_or_none()
        await state.update_data(user_id=current_user.id)

        available_products = await get_available_products(session)
    logging.info(f"AVAILABLE PRODUCTS: {available_products}")

    message_text = RentStrings.RENT_STARTING_PROCESS[lang]

    available_types = set()

    # available_types = set()
    for product, remaining_quantity in available_products:
        # lesani yangi o'lchami qo'shilsa, ishga tushiramiz
        # if product.product_type.name == ProductTypeEnum.lesa.name:
        #     size_name = product.product_size.name
        #     product_name = RentStrings.CHOOSE_PRODUCT_KEYBOARD[lang][ProductTypeEnum.lesa.name][size_name]
        if product.product_type.name == ProductTypeEnum.taxta_opalubka.name:
            size_name = product.product_size.name
            product_name = RentStrings.CHOOSE_PRODUCT_KEYBOARD[lang][ProductTypeEnum.taxta_opalubka.name][size_name]

        else:
            product_name = RentStrings.CHOOSE_PRODUCT_KEYBOARD[lang][product.product_type.name]

        available_types.add(product.product_type.name)
        # real-time qoldiqni chiqaramiz
        if lang == "uzl":
            message_text += f"<b>{product_name}</b> - Qoldiq: <u>{remaining_quantity}</u>\n"
        elif lang == "uzk":
            message_text += f"<b>{product_name}</b> - Қолдиқ: <u>{remaining_quantity}</u>\n"
        elif lang == "rus":
            message_text += f"<b>{product_name}</b> - Остаток: <u>{remaining_quantity}</u>\n"

    logging.info(f"MESSAGE TEXT: {message_text}")

    # await state.set_state(RentStatus.lesa_size_choice)
    await state.set_state(RentStatus.product_choice)

    # print(f"AVAILABLE TYPES: {available_types}")
    # kb_label = [PRODUCT_TYPE_LABEL[lang][t] for t in available_types]
    kb = [PRODUCT_TYPE_LABEL[lang][t] for t in available_types]
    logging.info(f"KB: {kb}")
    await message.answer(
        text=message_text,
        reply_markup=build_select_keyboard(kb),

    )


@router.message(Command("rent", prefix="/!"))
async def handle_command_rent_not_admin(message: types.Message):
    lang = await get_user_language(message)
    await message.answer(
        {
            "uzl": "Sizga ruxsat yo'q ❌\nMa'lumotlar faqat admin uchun",
            "uzk": "Сизга рухсат йўқ ❌\nМаълумотлар фақат админ учун",
            "rus": "Вам запрещено ❌\nИнформация только для администратора.",
        }.get(lang, "Сизга рухсат йўқ ❌\nМаълумотлар фақат админ учун")
    )


@router.message(Command("cancel"), RentStatus())
@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel", RentStatus())
@router.message(F.text.casefold() == "cancel")
async def cancel_handle(message: types.Message, state: FSMContext) -> None:
    state_current = await state.get_state()
    if state_current is None:
        await message.answer(
            text=f"ОК, лекин ҳеч нарсани бошламаган эдик ҳали.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return
    await state.clear()
    await message.answer(
        text=f"Жараён <b><u>{state_current.split(':')[-1]}</u></b> қадамида тўхтатилди.",
        reply_markup=types.ReplyKeyboardRemove()
    )
