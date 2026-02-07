from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from database.config import get_allowed_tg_ids

# admin telegram_id lar

ALLOWED_TG_IDS = get_allowed_tg_ids()
print(get_allowed_tg_ids())


class AdminOnly(BaseFilter):
    # BaseFilter: xabar o'tkazash yoki o'tkazmaslik savoliga javob beradi

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        # __call__ — Python’da avtomatik chaqiriladigan funksiya.
        # event: xabar bo'lishi mumkin yoki CallbackQuery

        return event.from_user.id in ALLOWED_TG_IDS  # xabar yozgan user id raqami ro'yxatda bo'lsa, True, agar bo'lmasa False

