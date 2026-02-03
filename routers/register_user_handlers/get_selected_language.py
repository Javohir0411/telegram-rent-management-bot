import logging
from bot_strings.start_command_strings import StartStrings
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from keyboards.common_keyboards import choose_language_kb, build_select_keyboard
from states import Register
from utils.enums import LanguageEnum

logging.basicConfig(level=logging.INFO)
router = Router(name=__name__)




@router.message(F.text, Register.language)
async def handle_selected_language(message: types.Message, state: FSMContext):
    try:
        language_enum = LanguageEnum(message.text)
    except ValueError:
        await message.reply(
            text="Илтимос, қуйидаги тиллардан бирини танланг⬇️",
            reply_markup=build_select_keyboard(LanguageEnum)
        )
        return

    await state.update_data(selected_language=language_enum.name)
    await state.set_state(Register.full_name)

    lang = language_enum.name
    message_text = StartStrings.SELECT_LANGUAGE[lang]

    if lang == "uzl":
        await message.answer(
            text=message_text,
            reply_markup=types.ReplyKeyboardRemove(),
        )

    elif lang == "uzk":
        await message.answer(
            text=message_text,
            reply_markup=types.ReplyKeyboardRemove(),
        )

    elif lang == "rus":
        await message.answer(
            text=message_text,
            reply_markup=types.ReplyKeyboardRemove(),
        )


# @router.message(Register.language)
# async def handle_invalid_language(message: types.Message):
#     await message.reply(
#         text="Iltimos, quyidagi tillardan birini tanlang⬇️",
#         reply_markup=choose_language_kb()
#     )
