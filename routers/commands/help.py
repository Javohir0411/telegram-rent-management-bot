from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

from bot_strings.help_command_strings import HelpStrings
from database.session import get_user_language
import logging

from utils.admin_only import AdminOnly

logging.basicConfig(level=logging.INFO)
router = Router(name=__name__)


@router.message(Command("help", prefix="/!"))
async def handle_command_help(message: types.Message):
    logging.info(f"{message.text} COMMAND ISHINI BOSHLADI")
    lang = await get_user_language(message)

    message_text = HelpStrings.TEXT.get(lang, HelpStrings.TEXT["uzk"])

    await message.answer(
        text=message_text,
        reply_markup=ReplyKeyboardRemove()
    )
    logging.info(f"{message.text} COMMAND ISHINI YAKUNLADI")

