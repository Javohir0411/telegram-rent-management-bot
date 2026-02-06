from utils.enums import LanguageEnum
from aiogram.utils import markdown


class HelpStrings:
    TEXT = {
        LanguageEnum.uzl.name: (
            "🤖 <b>Bot nima qiladi?</b>\n\n"
            "Bu bot sizga xizmatlar bilan tez va qulay ishlash imkonini beradi.\n\n"
            "<b>Mavjud buyruqlar:</b>\n"
            "/start — Botni ishga tushirish\n"
            "/help — Yordam va qo‘llanma\n"
            "/rent - Ijaraga berish jarayonini boshlash\n"
            "/leased - Ijaraga berilganlarni ko'rish.\n"
            "/rent_report - Oraliq hisobotni olish.\n"
            "/pay_update - Ijarachining to'lov holatini yangilash.\n"
            "/total - Mahsulotlarni umumiy sonini ko'rish.\n"
            "/return - Ijaraga berilganlarni qaytarib olish.\n"
            "/settings - Sozlamalar.\n"
            "/cancel - Jarayonni to'xtatish va botni oddiy xolatga o'tkazish\n"
        ),

        LanguageEnum.uzk.name: (
            "🤖 <b>Бот нима қилади?</b>\n\n"
            "Бу бот сизга хизматлар билан тез ва қулай ишлаш имконини беради.\n\n"
            "<b>Мавжуд буйруқлар:</b>\n"
            "/start — Ботни ишга тушириш\n"
            "/help — Ёрдам ва қўлланма\n"
            "/rent - Ижарага бериш жараёнини бошлаш\n"
            "/leased - Ижарага берилганларни кўриш.\n"
            "/rent_report - Оралиқ ҳисоботни олиш.\n"
            "/pay_update - Ижарачининг тўлов ҳолатини янгилаш.\n"
            "/total - Маҳсулотларни умумий сонини кўриш.\n"
            "/return - Ижарага берилганларни қайтариб олиш.\n"
            "/settings - Созламалар.\n"
            "/cancel - Жараённи тўхтатиш ва ботни оддий холатга ўтказиш\n"
        ),

        LanguageEnum.rus.name: (
            "🤖 <b>Что делает бот?</b>\n\n"
            "Этот бот помогает вам быстро и удобно пользоваться сервисом.\n\n"
            "<b>Доступные команды:</b>\n"
            "/start — Запустить бота\n"
            "/help — Справка\n"
            "/rent - Начать процесс аренды\n"
            "/leased - Осмотр арендованных объектов недвижимости.\n"
            "/rent_report - Получить промежуточный отчет.\n"
            "/pay_update - Обновить статус платежа арендатора.\n"
            "/return - Возврат арендованного имущества.\n"
            "/settings - Настройки.\n"
            "/cancel - Остановите процесс и верните бота в обычный режим.\n"
        ),
    }
