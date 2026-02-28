from aiogram.filters.callback_data import CallbackData
from enum import Enum, IntEnum, auto, StrEnum
from sys import prefix



class LanguageEnum(StrEnum):
    uzl = "O'zbek tili (lotin)"
    uzk = "Ўзбек тили (крилл)"
    rus = "Русский язык"


class ProductTypeEnum(StrEnum):
    lesa = "lesa"
    monolit = "monolit"
    taxta_opalubka = "taxta_opalubka"
    metal_opalubka = "metal_opalubka"

class ProductSizeEnum(StrEnum):
    katta = "katta"
    orta = "orta"
    kichik = "kichik"
    four_meters = "four_meters"
    three_meters = "three_meters"
    two_meters = "two_meters"
    one_meter = "one_meter"


class RentStatusEnum(StrEnum):
    active = "Ижарада"
    returned = "Қайтарилган"


class PaymentStatusEnum(StrEnum):
    full_paid = "Тўлиқ ✅"
    part_paid = "Қисман ⚠️"
    not_paid = "Тўланмаган ❌"


class SettingsActions(IntEnum):
    language = auto()
    renter = auto()
    products = auto()
    user_info = auto()


class SettingsCB(CallbackData, prefix="settings"):
    action: SettingsActions


class StatusActions(IntEnum):
    full_paid = auto()
    part_paid = auto()
    not_paid = auto()


class StatusCB(CallbackData, prefix="status"):
    action: StatusActions


"""
CREATE TYPE ProductTypeEnum AS ENUM ('lesa', 'monolit', 'taxta');
CREATE TYPE ProductSizeEnum AS ENUM ('katta', 'orta', 'kichik', 'none');
CREATE TYPE RentStatusEnum AS ENUM ('full_paid', 'part_paid', 'not_paid');
CREATE TYPE LanguageEnum AS ENUM ('uzl', 'uzk', 'rus');
"""
