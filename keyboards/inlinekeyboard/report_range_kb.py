from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def report_range_kb(lang: str) -> InlineKeyboardMarkup:
    t = {
        "uzl": {
            "today": "Bugun",
            "week": "Bir haftalik",
            "month": "Bir oylik",
            "year": "Bir yillik",
            "custom": "O‘zim kiritaman",
        },
        "uzk": {
            "today": "Бугун",
            "week": "Бир ҳафталик",
            "month": "Бир ойлик",
            "year": "Бир йиллик",
            "custom": "Ўзим киритаман",
        },
        "rus": {
            "today": "Сегодня",
            "week": "За неделю",
            "month": "За месяц",
            "year": "За год",
            "custom": "Ввести вручную",
        }
    }.get(lang, {
        "today": "Бугун",
        "week": "Бир ҳафталик",
        "month": "Бир ойлик",
        "year": "Бир йиллик",
        "custom": "Ўзим киритаман",
    })

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["today"], callback_data="rent_report_range:today")],
        [InlineKeyboardButton(text=t["week"], callback_data="rent_report_range:week")],
        [InlineKeyboardButton(text=t["month"], callback_data="rent_report_range:month")],
        [InlineKeyboardButton(text=t["year"], callback_data="rent_report_range:year")],
        [InlineKeyboardButton(text=t["custom"], callback_data="rent_report_range:custom")],
    ])
