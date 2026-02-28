from database.products.available_product import get_available_products
from database.session import async_session_maker, get_user_language
from bot_strings.rent_command_strings import RentStrings
from utils.current_user import get_current_user
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from bot_strings.enum_str import SIZE_LABEL
from utils.enums import ProductTypeEnum
from keyboards.common_keyboards import (
    build_lesa_keyboard,
    build_taxta_keyboard,
    build_metal_keyboard,
    TAXTA_SIZES,
    LESA_SIZES,
    METAL_SIZES
)
from aiogram import Router, types
from states import RentStatus
import logging

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.message(StateFilter(RentStatus.lesa_size_choice))
@router.message(StateFilter(RentStatus.taxta_size_choice))
@router.message(StateFilter(RentStatus.metal_size_choice))
async def handle_selected_size(message: types.Message, state: FSMContext):
    selected_size = (message.text or "").strip()
    lang = await get_user_language(message)

    text_invalid_size = RentStrings.INSERT_INVALID_SIZE[lang]
    text_quantity = RentStrings.INSERT_QUANTITY_PRODUCT[lang]

    current_state = await state.get_state()

    # 1) Qaysi state -> qaysi allowed sizes + keyboard
    if current_state == RentStatus.lesa_size_choice.state:
        allowed_sizes = LESA_SIZES
        kb = build_lesa_keyboard(lang)
    elif current_state == RentStatus.taxta_size_choice.state:
        allowed_sizes = TAXTA_SIZES
        kb = build_taxta_keyboard(lang)
    elif current_state == RentStatus.metal_size_choice.state:
        allowed_sizes = METAL_SIZES
        kb = build_metal_keyboard(lang)
    else:
        # bu holat amalda bo'lmasligi kerak
        await message.answer(text=text_invalid_size, reply_markup=ReplyKeyboardRemove())
        return

    # 2) Button text -> enum.value (string) mapping (masalan "2 metrlik" -> "two_meters")
    text_to_value = {SIZE_LABEL[lang][e]: e.value for e in allowed_sizes}

    # 3) Noto'g'ri matn kiritilsa qayta keyboard
    if selected_size not in text_to_value:
        await message.answer(text=text_invalid_size, reply_markup=kb)
        return

    size_value = text_to_value[selected_size]  # masalan "two_meters"

    # 4) Current user (tenant_id kerak)
    current_user = await get_current_user(message)
    if not current_user:
        await message.answer(
            {"uzl": "Avval ro‘yxatdan o‘ting: /start",
             "uzk": "Аввал рўйхатдан ўтинг: /start",
             "rus": "Сначала зарегистрируйтесь: /start"}.get(lang, "Avval /start"),
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # 5) State'dan oxirgi tanlangan product_type ni olamiz
    data = await state.get_data()
    rent_info = data.get("rent_info", [])

    if not rent_info:
        await message.answer(
            {"uzl": "Jarayon buzildi. Iltimos, /rent dan qayta boshlang.",
             "uzk": "Жараён бузилди. Илтимос, /rent дан қайта бошланг.",
             "rus": "Процесс сбился. Пожалуйста, начните заново: /rent."}.get(lang),
            reply_markup=ReplyKeyboardRemove()
        )
        return

    last_type_value = rent_info[-1].get("product_type")  # string: "taxta_opalubka" yoki "lesa"
    if not last_type_value:
        await message.answer(
            {"uzl": "Jarayon buzildi. /rent dan qayta boshlang.",
             "uzk": "Жараён бузилди. /rent дан қайта бошланг.",
             "rus": "Процесс сбился. Начните заново: /rent."}.get(lang),
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # string -> enum
    try:
        last_type_enum = ProductTypeEnum(last_type_value)
    except ValueError:
        await message.answer(
            {"uzl": "Noma'lum mahsulot turi. /rent dan qayta boshlang.",
             "uzk": "Номаълум маҳсулот тури. /rent дан қайта бошланг.",
             "rus": "Неизвестный тип товара. Начните заново: /rent."}.get(lang),
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # 6) DB dan shu tenant bo'yicha qoldiqni topamiz (type+size kesimida)
    async with async_session_maker() as session:
        available_products = await get_available_products(session, tenant_id=current_user.tenant_id)

    selected_product = None
    selected_remaining = None

    for p, rem in available_products:
        # product_size DBda enum bo'lishi mumkin; p.product_size.value bilan solishtiramiz
        if p.product_type == last_type_enum and p.product_size is not None and p.product_size.value == size_value:
            selected_product = p
            selected_remaining = rem
            break

    # 7) Topilmasa: ehtimol qoldiq 0 bo'lib qolgan yoki mismatch
    if not selected_product:
        await message.answer(
            {"uzl": "❌ Bu o‘lcham bo‘yicha qoldiq topilmadi. Boshqa o‘lcham tanlang.",
             "uzk": "❌ Бу ўлчам бўйича қолдиқ топилмади. Бошқа ўлчам танланг.",
             "rus": "❌ По этому размеру нет остатка. Выберите другой размер."}.get(lang),
            reply_markup=kb
        )
        return

    # 8) rent_info oxirgi itemga size + product_id yozamiz
    rent_info[-1]["product_size"] = size_value  # string: "two_meters"
    rent_info[-1]["product_id"] = selected_product.id

    # quantity validatsiya uchun selected_remaining ni statega saqlab qo'yamiz
    await state.update_data(rent_info=rent_info, selected_remaining=selected_remaining)

    # 9) Keyingi qadam: quantity
    await state.set_state(RentStatus.quantity)
    await message.answer(text=text_quantity, reply_markup=ReplyKeyboardRemove())
