from keyboards.common_keyboards import skip_rent_end_date
from bot_strings.rent_command_strings import RentStrings
from database.session import get_user_language
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from utils.filter_date import is_date
from states import RentStatus
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
router = Router(name=__name__)


@router.message(F.text.func(is_date), RentStatus.start_date)
async def handle_rent_start_date(message: types.Message, state: FSMContext):
    start_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    await state.update_data(start_date=start_date)
    lang = await get_user_language(message)

    data = await state.get_data()
    logging.info(f"START DATE QO'SHILDI: {data}")
    logging.info(f"START DATE QO'SHILDI: {data['start_date']}")
    # text = RentStrings.GET_RENT_END_DATE[lang]

    await state.set_state(RentStatus.end_date)
    await message.answer(
        {
            "uzl": "Ijarani tugash sanasini kiriting. Masalan: `01.01.2026`\n\n"
                   "Yoki *O'tkazib yuborish ⏭️* tugmasini bosing.\n"
                   "Bu yo'l orqali ijarani tugash sanasini kiritishni keyinroqqa qoldirasiz.",

            "uzk": "Ижарани тугаш санасини киритинг. Масалан: `01.01.2026`\n\n"
                   "Ёки *Ўтказиб юбориш ⏭️* тугмасини босинг."
                   "Бу йўл орқали ижарани тугаш санасини киритишни кейинроққа қолдирасиз.\n",

            "rus": "Введите дату окончания аренды. Например: `01.01.2026`\n\n"
                   "Или нажмите кнопку *Пропустить ⏭️*.\n"
                   "Это позволит вам отложить ввод даты окончания срока аренды.\n"

        }.get(lang, "Ижарани тугаш санасини киритинг. Масалан: `01.01.2026`\n\n"
                    "Bu yo'q orqali ijarani tugash sanasini kiritishni keyinroqqa qoldirasiz.\n"
                    "Ёки *Ўтказиб юбориш ⏭️* тугмасини босинг."),
        reply_markup=skip_rent_end_date(lang),
        parse_mode="Markdown",
    )


@router.message(F.text.func(is_date), RentStatus.end_date)
async def handle_rent_end_date(message: types.Message, state: FSMContext):
    end_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    lang = await get_user_language(message)

    data = await state.get_data()
    start_date = data.get("start_date")

    if start_date and end_date < start_date:
        lang = await get_user_language(message)
        await message.reply(
            {
                "uzl": f"❌ Tugash sanasi boshlanish sanasidan kichik bo‘lishi mumkin emas.\n"
                       f"Boshlanish: `{start_date.strftime('%d.%m.%Y')}`\n"
                       f"Qaytadan tugash sanasini kiriting yoki *O'tkazib yuborish ⏭️* tugmasini bosing.",
                "uzk": f"❌ Тугаш санаси бошланиш санасидан кичик бўлиши мумкин эмас.\n"
                       f"Бошланиш: `{start_date.strftime('%d.%m.%Y')}`\n"
                       f"Қайтадан тугаш санасини киритинг ёки *Ўтказиб юбориш ⏭️* тугмасини босинг.",
                "rus": f"❌ Дата окончания не может быть меньше даты начала.\n"
                       f"Начало: `{start_date.strftime('%d.%m.%Y')}`\n"
                       f"Введите дату окончания заново или нажмите *Пропустить ⏭️*.",
            }.get(lang, f"❌ Тугаш санаси бошланиш санасидан кичик бўлиши мумкин эмас.\n"
                        f"Бошланиш: `{start_date.strftime('%d.%m.%Y')}`\n"
                        f"Қайтадан тугаш санасини киритинг ёки Skip босинг."),
            reply_markup=skip_rent_end_date(lang),
            parse_mode="Markdown",
        )
        return

    await state.update_data(end_date=end_date)
    data = await state.get_data()
    logging.info(f"END DATE QO'SHILDI: {data}")
    logging.info(f"END DATE QO'SHILDI: {data['end_date']}")

    text = RentStrings.LOCATION_REQUEST[lang]
    await state.set_state(RentStatus.location_request)
    await message.answer(
        text=text,
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(F.text.in_({"O'tkazib yuborish ⏭️", "Ўтказиб юбориш ⏭️", "Пропустить ⏭️"}), RentStatus.end_date)
async def handle_rent_end_date_skip(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)
    await state.update_data(end_date=None)
    text = RentStrings.LOCATION_REQUEST[lang]
    await state.set_state(RentStatus.location_request)
    await message.answer(
        text=text,
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(RentStatus.start_date)
async def handle_rent_end_date(message: types.Message):
    lang = await get_user_language(message)
    await message.reply(
        {
            "uzl": "❌ Sana noto'g'ri kiritildi.\n"
                   "Iltimos, sanani `DD.MM.YYYY` formatida kiriting.\n"
                   "Masalan: `01.01.2026`\n",

            "uzk": "❌ Сана нотўғри киритилди.\n"
                   "Илтимос, санани `DD.MM.YYYY` форматида киритинг.\n"
                   "Масалан: `01.01.2026`\n",

            "rus": "❌ Неверный формат даты.\n"
                   "Пожалуйста, введите дату в формате `DD.MM.YYYY`.\n"
                   "Например: `01.01.2026`\n"

        }.get(lang, "❌ Сана нотўғри киритилди.\n"
                    "Илтимос, санани `DD.MM.YYYY` форматида киритинг.\n"
                    "Масалан: `01.01.2026`\n"),
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )


@router.message(RentStatus.end_date)
async def handle_rent_end_date(message: types.Message):
    lang = await get_user_language(message)
    await message.reply(
        {
            "uzl": "❌ Sana noto'g'ri kiritildi.\n"
                   "Iltimos, sanani `DD.MM.YYYY` formatida kiriting.\n"
                   "Masalan: `01.01.2026`\n\n"
                   "Yoki O'tkazib yuborish ⏭️ tugmasini bosing 👇",

            "uzk": "❌ Сана нотўғри киритилди.\n"
                   "Илтимос, санани `DD.MM.YYYY` форматида киритинг.\n"
                   "Масалан: `01.01.2026`\n\n"
                   "Ёки *Ўтказиб юбориш ⏭️* тугмасини босинг.",

            "rus": "❌ Неверный формат даты.\n"
                   "Пожалуйста, введите дату в формате `DD.MM.YYYY`.\n"
                   "Например: `01.01.2026`\n\n"
                   "Или нажмите кнопку *Пропустить ⏭️*."

        }.get(lang, "❌ Сана нотўғри киритилди.\n"
                    "Илтимос, санани `DD.MM.YYYY` форматида киритинг.\n"
                    "Масалан: `01.01.2026`\n\n"
                    "Ёки *Ўтказиб юбориш ⏭️* тугмасини босинг."),

        reply_markup=skip_rent_end_date(lang),
        parse_mode="Markdown",
    )
