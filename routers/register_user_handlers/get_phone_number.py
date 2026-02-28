from utils.get_user_from_db import get_user_by_telegram_or_phone
from keyboards.get_phone_number import get_phone_number_kb
from bot_strings.start_command_strings import StartStrings
from database.session import async_session_maker
from bot_strings.bot_command import BotCommands
from database.config import get_allowed_tg_ids
from aiogram.types import BotCommandScopeChat
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError
from aiogram import Router, F, types
from db.crud_user import create_user
from aiogram.utils import markdown
from states import Register
import logging

logging.basicConfig(level=logging.INFO)
router = Router(name=__name__)

ADMIN_IDS = set(get_allowed_tg_ids())
ADMIN_TENANT_ID = 1


@router.message(F.contact, Register.phone_number)
async def handle_phone_number(message: types.Message, state: FSMContext):
    user_phone_number = message.contact.phone_number
    telegram_id = message.from_user.id

    await state.update_data(user_phone_number=user_phone_number)
    data = await state.get_data()

    lang = data.get("selected_language") or "uzk"

    # tenant_id endi hech qachon None bo'lmaydi
    tenant_id = ADMIN_TENANT_ID if telegram_id in ADMIN_IDS else None
    logging.info(f"DBG telegram_id={telegram_id} tenant_id_var={tenant_id} type={type(tenant_id)}")
    async with async_session_maker() as session:
        existing_user = await get_user_by_telegram_or_phone(
            db=session,
            telegram_id=telegram_id,
            phone_number=user_phone_number,
            tenant_id=tenant_id
        )

        if existing_user:
            message_text = StartStrings.EXISTING_USER.get(lang, StartStrings.EXISTING_USER["uzk"])
            await message.answer(message_text, reply_markup=types.ReplyKeyboardRemove())
            await state.clear()
            return

        try:
            await create_user(
                db=session,
                telegram_id=telegram_id,
                user_fullname=data["user_fullname"],
                user_phone_number=data["user_phone_number"],
                selected_language=lang,
                tenant_id=tenant_id,
            )
        except IntegrityError as e:
            await session.rollback()
            err = str(e.orig) if getattr(e, "orig", None) else str(e)

            if "uq_user_tenant_telegram" in err:
                await message.answer(
                    StartStrings.EXISTING_USER.get(lang, StartStrings.EXISTING_USER["uzk"]),
                    reply_markup=types.ReplyKeyboardRemove()
                )
                await state.clear()
                return

            if "uq_user_tenant_phone" in err:
                await message.answer(
                    {
                        "uzl": "Bu telefon raqami allaqachon ro'yxatdan o'tgan.",
                        "uzk": "Бу телефон рақами аллақачон рўйхатдан ўтган.",
                        "rus": "Этот номер телефона уже зарегистрирован.",
                    }.get(lang),
                    reply_markup=types.ReplyKeyboardRemove()
                )
                await state.clear()
                return

            await message.answer(
                {
                    "uzl": "Saqlashda xatolik yuz berdi.",
                    "uzk": "Сақлашда хато юз берди.",
                    "rus": "Ошибка при сохранении."
                }.get(lang),
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.clear()
            return

    # komandalarni o'rnatish (qolsin)
    commands = BotCommands.COMMANDS.get(lang, BotCommands.COMMANDS["uzk"])
    await message.bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=telegram_id))

    message_text = StartStrings.GET_PHONE_NUMBER.get(lang, StartStrings.GET_PHONE_NUMBER["uzk"]).format(
        user_phone_number=markdown.hbold(data["user_phone_number"]),
        user_fullname=markdown.hbold(data["user_fullname"]),
    )
    await message.answer(text=message_text, reply_markup=types.ReplyKeyboardRemove())

    # ombor lokatsiyasini so'raymiz
    await state.set_state(Register.warehouse_location)
    await message.answer(
        {
            "uzl": "📍 Omboringiz lokatsiyasini yuboring (Location).",
            "uzk": "📍 Омборингиз локациясини юборинг (Location).",
            "rus": "📍 Отправьте локацию склада (Location).",
        }.get(lang),
        reply_markup=types.ReplyKeyboardRemove()
    )
    return


@router.message(Register.phone_number)
async def handle_invalid_phone_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("selected_language")
    message_text = StartStrings.GET_INVALID_PHONE_NUBER[lang]
    kb = await get_phone_number_kb(state)

    await message.reply(text=message_text, reply_markup=kb)
