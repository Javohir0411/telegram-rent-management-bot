from aiogram.types import BotCommand
from utils.enums import LanguageEnum


class BotCommands:
    COMMANDS = {
        LanguageEnum.uzl.name: [
            BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="help", description="Yordam olish"),
            BotCommand(command="rent", description="Ijaraga berishni boshlash"),
            BotCommand(command="leased", description="Ijaraga berilgan mahsulotlarni ko'rish"),
            BotCommand(command="rent_report", description="Oraliq hisobotni olish"),
            BotCommand(command="total", description="Mahsulotlarni umumiy sonini ko'rish"),
            BotCommand(command="return", description="Ijaraga berilganlarni qaytarib olish"),
            BotCommand(command="pay_update", description="Ijarachining to'lov holatini yangilash."),
            BotCommand(command="add_product", description="Mahsulot qo'shish"),
            BotCommand(command="settings", description="Sozlamalar"),
            BotCommand(command="cancel", description="Jarayonni to'xtatish va botni oddiy xolatga o'tkazish"),
        ],
        LanguageEnum.uzk.name: [
            BotCommand(command="start", description="Ботни ишга тушириш"),
            BotCommand(command="help", description="Ёрдам олиш"),
            BotCommand(command="rent", description="Ижарага бериш жараёнини бошлаш"),
            BotCommand(command="leased", description="Ижарага берилган маҳсулотларни кўриш"),
            BotCommand(command="rent_report", description="Оралиқ ҳисоботни олиш"),
            BotCommand(command="total", description="Маҳсулотларни умумий сонини кўриш"),
            BotCommand(command="return", description="Ижарага берилганларни қайтариб олиш"),
            BotCommand(command="pay_update", description="Ижарачининг тўлов ҳолатини янгилаш."),
            BotCommand(command="add_product", description="Маълумотлар базасига маҳсулот қўшиш"),
            BotCommand(command="settings", description="Созламалар"),
            BotCommand(command="cancel", description="Жараённи тўхтатиш ва ботни оддий холатга ўтказиш"),
        ],
        LanguageEnum.rus.name: [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="help", description="Получить помощь"),
            BotCommand(command="rent", description="Начать процесс аренды"),
            BotCommand(command="leased", description="Посмотреть продукты для аренды"),
            BotCommand(command="rent_report", description="Получить промежуточный отчет"),
            BotCommand(command="total", description="Посмотреть общее количество товаров"),
            BotCommand(command="return", description="Возврат арендованного имущества"),
            BotCommand(command="pay_update", description="Обновить статус платежа арендатора."),
            BotCommand(command="add_product", description="Добавить товар в базу данных"),
            BotCommand(command="settings", description="Настройки"),
            BotCommand(command="cancel", description="Остановите процесс и верните бота в обычный режим."),
        ],
    }
