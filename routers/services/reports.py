from routers.services.rent_report_query import get_rents_for_report
from database.session import async_session_maker, get_user_language
from routers.services.build_excel import build_excel
from aiogram.types import FSInputFile, CallbackQuery
from datetime import datetime, timedelta, date
from aiogram.fsm.context import FSMContext
from utils.admin_only import AdminOnly
from aiogram.types import FSInputFile
from datetime import datetime, date
from aiogram import Router, types
from states import ReportState
from zoneinfo import ZoneInfo
from sqlalchemy import select
from db.models import User
from datetime import date
from aiogram import F
import logging
import os

logging.basicConfig(level=logging.INFO)
router = Router(name=__name__)


def get_today_tashkent() -> date:
    return datetime.now().date()


def calc_range(action: str) -> tuple[date, date]:
    today = get_today_tashkent()

    if action == "today":
        return today, today
    if action == "week":
        return today - timedelta(days=6), today
    if action == "month":
        return today - timedelta(days=29), today
    if action == "year":
        return today - timedelta(days=364), today

    raise ValueError("Unknown range action")


async def generate_and_send_report(
        message: types.Message,
        state: FSMContext,
        lang: str,
        start_date: date,
        end_date: date,
        requester_tg_id,
):
    async with async_session_maker() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == requester_tg_id)
        )
        if not user:
            await message.answer("❗Сиз базада рўйхатдан ўтмагансиз.")
            return

        rents = await get_rents_for_report(
            session=session,
            tenant_id=user.tenant_id,  # ✅ shu yerda tenant olinadi
            user_db_id=user.id,
            start_date=start_date,
            end_date=end_date
        )

    if not rents:
        await message.answer(
            {
                "uzl": "📭 Bu sana oralig‘ida ma’lumot topilmadi.",
                "uzk": "📭 Бу сана оралиғида маълумот топилмади.",
                "rus": "📭 Информация по данному диапазону не найдена.",
            }.get(lang, "📭 Бу сана оралиғида маълумот топилмади.")
        )
        return

    stream = build_excel(lang, rents, start_date, end_date)

    os.makedirs("tmp", exist_ok=True)
    filename = f"rent_report_{start_date.isoformat()}_to_{end_date.isoformat()}.xlsx"
    tmp_path = os.path.join("tmp", filename)

    with open(tmp_path, "wb") as f:
        f.write(stream.getvalue())

    caption = {
        "uzl": f"📊 Ijara hisobot\n`{start_date.isoformat()} — {end_date.isoformat()}`\nJami: {len(rents)} ta yozuv",
        "uzk": f"📊 Ижара ҳисобот\n`{start_date.isoformat()} — {end_date.isoformat()}`\nЖами: {len(rents)} та ёзув",
        "rus": f"📊 Отчет об аренде\n`{start_date.isoformat()} — {end_date.isoformat()}`\nВсего: {len(rents)} записей",
    }.get(lang, f"📊 Ижара ҳисобот\n`{start_date.isoformat()} — {end_date.isoformat()}`\nЖами: {len(rents)} та ёзув")

    await message.answer_document(
        document=FSInputFile(tmp_path),
        caption=caption,
        parse_mode="Markdown"
    )

    try:
        os.remove(tmp_path)
    except OSError:
        pass

    await state.clear()


@router.callback_query(F.data.startswith("rent_report_range:"))
async def rent_report_range_callback(call: types.CallbackQuery, state: FSMContext):
    lang = await get_user_language(call)
    logging.info(f"RENT REPORT RANGE: {lang}")

    action = call.data.split(":")[1]  # today/week/month/year/custom

    if action == "custom":
        await call.message.answer(
            {
                "uzl": "📅 Sana oralig‘ini yuboring:\n`DD.MM.YYYY DD.MM.YYYY`\nMasalan: `01.01.2026 10.01.2026`",
                "uzk": "📅 Сана оралиғини юборинг:\n`ДД.ММ.ГГГГ ДД.ММ.ГГГГ`\nМасалан: `01.01.2026 10.01.2026`",
                "rus": "📅 Укажите диапазон дат:\n`ДД.ММ.ГГГГ ДД.ММ.ГГГГ`\nНапример: `01.01.2026 10.01.2026`",
            }.get(lang, "📅 Сана оралиғини юборинг:\n`ДД.ММ.ГГГГ ДД.ММ.ГГГГ`\nМасалан: `01.01.2026 10.01.2026`"),
            parse_mode="Markdown"
        )
        await state.set_state(ReportState.get_start_end_dates)
        await call.answer()
        return

    # avtomatik range
    start_date, end_date = calc_range(action)

    # sizdagi rent_report_dates_input() ichidagi “hisobot yaratish” logikasini qayta ishlatamiz:
    await call.answer("✅")  # loadingni to‘xtatadi

    # shu yerda bitta “umumiy funksiya” yaxshi bo‘ladi,
    # lekin tezkor qilish uchun rent_report_dates_input() ichidagi
    # DB -> build_excel -> send doc qismini alohida funksiya qilib ko‘chiring.
    await generate_and_send_report(call.message, state, lang, start_date, end_date, requester_tg_id=call.from_user.id)


def parse_two_dates(text: str, lang: str) -> tuple[date, date]:
    parts = text.strip().split()  # yuborilgan matnni boshi va oxiridagi bo'shliqni olib tashlaydi va o'rtasidagi bo'sh joydan ikkiga bo'ladi
    if len(parts) != 2:  # Agar xabar 2 ga bo'linmasa, ya'ni, sanalar alohida-alohida yuborilmasa, XATOLIK chiqadi
        raise ValueError(
            {
                "uzl": "Ikkita sana yuborilishi kerak!",
                "uzk": "Иккита сана юборилиши керак!",
                "rus": "Необходимо прислать две даты!",
            }[lang]
        )
    d1 = datetime.strptime(parts[0], "%d.%m.%Y").date()  # birinchi qismini faqat sanasini oladi, vaqtni olmaydi
    d2 = datetime.strptime(parts[1], "%d.%m.%Y").date()  # bu ham xuddi shunday 👆
    if d2 < d1:  # agar user sananni o'rnini almashtirib qo'ysa:
        d1, d2 = d2, d1  # o'rnini almashtirib, to'g'irlab qo'yadi
    return d1, d2  # Natija


@router.message(ReportState.get_start_end_dates)
async def rent_report_dates_input(message: types.Message, state: FSMContext):
    lang = await get_user_language(message)

    try:
        start_date, end_date = parse_two_dates(message.text, lang)
    except ValueError as a:
        logging.info(f"REPORT DATES INPUT EXCEPTION: {a}")
        await message.answer(
            {
                "uzl": f"❌ Xatolik! Noto'g'ri ma'lumot yuborildi.\n\n✅ To‘g‘ri format:\n`01.01.2026 10.01.2026`",
                "uzk": f"❌ Хатолик! Нотўғри маълумот юборилди.\n\n✅ Тўғри формат:\n`01.01.2026 10.01.2026`",
                "rus": f"❌ Ошибка! Отправлена неверная информация.\n\n✅ Правильный формат:\n`01.01.2026 10.01.2026`",
            }[lang],
            parse_mode="Markdown"
        )
        return
    except Exception as e:
        logging.info(f"REPORT DATES INPUT EXCEPTION: {e}")
        await message.answer(
            {
                "uzl": "❌ Sana formati noto‘g‘ri.\n\n✅ To‘g‘ri format:\n`01.01.2026 10.01.2026`",
                "uzk": "❌ Сана формати нотўғри.\n\n✅ Тўғри формат:\n`01.01.2026 10.01.2026`",
                "rus": "❌ Неверный формат даты.\n\n✅ Правильный формат:\n`01.01.2026 10.01.2026`",
            }[lang],
            parse_mode="Markdown"
        )
        return

    await generate_and_send_report(message, state, lang, start_date, end_date, requester_tg_id=message.from_user.id)

