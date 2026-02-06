import logging

from aiogram import Router, types
from aiogram.types import BotCommandScopeChat
from sqlalchemy import update

from bot_strings.bot_command import BotCommands
from database.session import async_session_maker
from db.models import User

from keyboards.inlinekeyboard.language_kb import LanguageCB
from utils.enums import LanguageEnum

router = Router()


@router.callback_query(LanguageCB.filter())
async def change_language(
        call: types.CallbackQuery,
        callback_data: LanguageCB
):
    # callback_data.lang → value, masalan: "O'zbek tili (lotin)"
    # Uni enum orqali name ga o‘tkazamiz
    logging.info(f"CHANGE LANGUAGE CALLBACK DATA: {callback_data}")
    logging.info(f"CHANGE LANGUAGE CALLBACK DATA.LANG: {callback_data.lang}")
    lang_enum = LanguageEnum(callback_data.lang)  # value → enum
    logging.info(f"CHANGE LANGUAGE LANG ENUM: {lang_enum}")

    lang_name = lang_enum.name  # "uzl"
    logging.info(f"CHANGE LANGUAGE LANG NAME: {lang_name}")
    async with async_session_maker() as session:
        await session.execute(
            update(User)
            .where(User.telegram_id == call.from_user.id)
            .values(selected_language=lang_name)  # DB da 'uzl' saqlanadi
        )

        commands = BotCommands.COMMANDS.get(lang_name, BotCommands.COMMANDS["uzk"])
        await call.message.bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=call.from_user.id))
        await session.commit()

    await call.message.edit_text(
        {
            "uzl": f"✅ Til muvaffaqiyatli o‘zgartirildi: {lang_enum.value}",
            "uzk": f"✅ Тил муваффақиятли ўзгартирилди: {lang_enum.value}",
            "rus": f"✅ Язык успешно изменен: {lang_enum.value}",
        }[lang_name]
    )
    await call.answer()
