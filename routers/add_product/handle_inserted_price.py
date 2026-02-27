from typing import Optional

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database.products.add_product_to_db import create_or_update_product
from database.session import async_session_maker, get_user_language
from states import AddProductState
from utils.enums import ProductTypeEnum, ProductSizeEnum
from bot_strings.enum_str import SIZE_LABEL
from utils.get_user_from_db import get_user_by_telegram_or_phone

router = Router(name=__name__)


@router.message(AddProductState.insert_product_price, F.text.regexp(r"^\d+$"))
async def handle_inserted_product_price_ok(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)

    price = int(message.text)
    if price <= 0:
        await message.answer(
            text={
                "uzl": "Narx 0 dan katta bo‘lishi kerak. Qaytadan kiriting (faqat raqam).",
                "uzk": "Нарх 0 дан катта бўлиши керак. Қайтадан киритинг (фақат рақам).",
                "rus": "Цена должна быть больше 0. Введите заново (только цифры).",
            }.get(lang),
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    await state.update_data(insert_product_price=price)
    data = await state.get_data()
    print(f"UMUMIY OXIRGI MA'LUMOTLAR: {data}")

    tenant_id = data.get("tenant_id")
    product_type: Optional[ProductTypeEnum] = data.get("inserted_product_type")
    product_size: Optional[ProductSizeEnum] = data.get("inserted_product_size")
    quantity = data.get("insert_product_quantity")
    product_name = data.get("inserted_product_name", "mahsulot")

    if tenant_id is None:
        telegram_id = message.from_user.id

        async with async_session_maker() as session:
            user = await get_user_by_telegram_or_phone(session, telegram_id)

        if user is None:
            await message.answer(
                text={
                    "uzl": "Xatolik: foydalanuvchi bazadan topilmadi. /start qilib qaytadan urinib ko‘ring.",
                    "uzk": "Хатолик: фойдаланувчи базадан топилмади. /start қилиб қайтадан уриниб кўринг.",
                    "rus": "Ошибка: пользователь не найден в базе. Нажмите /start и попробуйте снова.",
                }.get(lang),
                reply_markup=types.ReplyKeyboardRemove(),
            )
            await state.clear()
            return

        tenant_id = user.tenant_id
        await state.update_data(tenant_id=tenant_id)

    if product_type is None or quantity is None:
        await message.answer(
            text={
                "uzl": "Xatolik: kerakli ma'lumotlar yetishmayapti. Qaytadan /add_product qilib ko‘ring.",
                "uzk": "Хатолик: керакли маълумотлар етишмаяпти. Қайтадан /add_product қилиб кўринг.",
                "rus": "Ошибка: не хватает данных. Попробуйте заново /add_product.",
            }.get(lang),
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.clear()
        return

    # --- DB ga saqlash ---
    async with async_session_maker() as session:
        try:
            product = await create_or_update_product(
                session,
                tenant_id=int(tenant_id),
                product_type=product_type,
                product_size=product_size,
                add_quantity=int(quantity),
                price_per_day=float(price),
            )
        except Exception as e:
            await message.answer(
                f"Xatolik: bazaga saqlashda muammo bo‘ldi.\n{type(e).__name__}: {e}",
                reply_markup=types.ReplyKeyboardRemove(),
            )
            return

    size_text = ""
    if product_size is not None:
        size_text = f"\nHajm: *{SIZE_LABEL[lang][product_size]}*"

    await message.answer(
        text={
            "uzl": f"✅ Saqlandi!\n"
                   f"Mahsulot: *{product_name}*"
                   f"{size_text}\n"
                   f"Miqdor qo‘shildi: *{quantity}*\n"
                   f"Kunlik narx: *{price}*\n"
                   f"Jami ombordagi: *{product.total_quantity}*",
            "uzk": f"✅ Сақланди!\n"
                   f"Маҳсулот: *{product_name}*"
                   f"{size_text}\n"
                   f"Миқдор қўшилди: *{quantity}*\n"
                   f"Кунлик нарх: *{price}*\n"
                   f"Жами омбордаги: *{product.total_quantity}*",
            "rus": f"✅ Сохранено!\n"
                   f"Товар: *{product_name}*"
                   f"{size_text}\n"
                   f"Добавлено: *{quantity}*\n"
                   f"Цена/день: *{price}*\n"
                   f"Итого на складе: *{product.total_quantity}*",
        }.get(lang),
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove(),
    )

    await state.clear()


@router.message(AddProductState.insert_product_price)
async def handle_inserted_product_price_bad(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    await message.answer(
        text={
            "uzl": "Narxni faqat raqam ko'rinishida kiriting!\nMasalan: 3000",
            "uzk": "Нархни фақат рақам кўринишида киритинг!\nМасалан: 3000",
            "rus": "Введите цену только цифрами!\nНапример: 3000",
        }.get(lang),
        reply_markup=types.ReplyKeyboardRemove(),
    )
