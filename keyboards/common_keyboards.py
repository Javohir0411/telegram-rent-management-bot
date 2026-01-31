from typing import Iterable

from bot_strings.enum_str import SIZE_LABEL
from bot_strings.rent_command_strings import RentStrings
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from utils.enums import ProductSizeEnum


def choose_language_kb():
    button_uzl = KeyboardButton(text="O'zbek tili (lotin) 🇺🇿")
    button_uzk = KeyboardButton(text="Ўзбек тили (крилл) 🇺🇿")
    button_rus = KeyboardButton(text="Русский язык 🇷🇺")
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [button_uzl],
            [button_uzk],
            [button_rus]
        ],
        resize_keyboard=True
    )
    return markup


def build_select_keyboard(options: Iterable[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for option in options:
        builder.button(text=option)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

LESA_SIZES = (ProductSizeEnum.katta, ProductSizeEnum.orta, ProductSizeEnum.kichik)

def build_lesa_keyboard(lang: str):
    return build_select_keyboard({SIZE_LABEL[lang][e]: e for e in LESA_SIZES})


TAXTA_SIZES = (
    ProductSizeEnum.four_meters,
    ProductSizeEnum.three_meters,
    ProductSizeEnum.two_meters,
    ProductSizeEnum.one_meter,
)


def build_taxta_keyboard(lang: str):
    return build_select_keyboard({SIZE_LABEL[lang][e]: e for e in TAXTA_SIZES})


METAL_SIZES = (
    ProductSizeEnum.three_meters,
)


def build_metal_keyboard(lang: str):
    return build_select_keyboard({SIZE_LABEL[lang][e]: e for e in METAL_SIZES})


# def build_location_type_kb(lang: str):
#     return build_select_keyboard({RentStrings.LOCATION_KB_TRANSLATION[lang][e.name]: e for e in LocationTypeEnum})


def build_yes_or_no_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Yes")
    builder.button(text="No")
    return builder.as_markup(resize_keyboard=True)
