from utils.enums import LanguageEnum, ProductTypeEnum, ProductSizeEnum


class RentStrings:
    RENT_STARTING_PROCESS = {
        LanguageEnum.uzl.name:
            "Unday bo'lsa, ijaraga berish jarayonini boshlaymiz.\n"
            "Quyidan, ijaraga bermoqchi bo'lgan mahsulotingizni tanlang\n\n",

        LanguageEnum.uzk.name:
            "Ундай бўлса, ижарага бериш жараёнини бошлаймиз.\n"
            "Қуйидан, ижарага бермоқчи бўлган маҳсулотингизни танланг\n\n",

        LanguageEnum.rus.name:
            "Затем мы начнем процесс аренды.\n"
            "Ниже выберите товар, который хотите арендовать.\n\n"
    }

    CHOOSE_PRODUCT_KEYBOARD = {
        LanguageEnum.uzl.name: {
            ProductTypeEnum.lesa.name:
                "Lesa"
                # ProductSizeEnum.katta.name: "Lesa Katta",
                # ProductSizeEnum.orta.name: "Lesa O'rta",
                # ProductSizeEnum.kichik.name: "Lesa Kichik",
            ,

            ProductTypeEnum.monolit.name: "Monolit ustun",
            ProductTypeEnum.taxta_opalubka.name: {
                ProductSizeEnum.four_meters.name: "4 metrlik taxta opalubka",
                ProductSizeEnum.three_meters.name: "3 metrlik taxta opalubka",
                ProductSizeEnum.two_meters.name: "2 metrlik taxta opalubka",
                ProductSizeEnum.one_meter.name: "1 metrlik taxta opalubka",
            },
            ProductTypeEnum.metal_opalubka.name:  "3 metrlik metal opalubka",
        },

        LanguageEnum.uzk.name: {
            ProductTypeEnum.lesa.name:
                "Леса"
                # ProductSizeEnum.katta.name: "Леса Катта",
                # ProductSizeEnum.orta.name: "Леса Ўрта",
                # ProductSizeEnum.kichik.name: "Леса Кичик",
            ,

            ProductTypeEnum.monolit.name: "Монолит устун",
            ProductTypeEnum.taxta_opalubka.name: {
                ProductSizeEnum.four_meters.name: "4 метрлик тахта опалубка",
                ProductSizeEnum.three_meters.name: "3 метрлик тахта опалубка",
                ProductSizeEnum.two_meters.name: "2 метрлик тахта опалубка",
                ProductSizeEnum.one_meter.name: "1 метрлик тахта опалубка",
            },
            ProductTypeEnum.metal_opalubka.name: "3 метрлик метал опалубка",
        },

        LanguageEnum.rus.name: {
            ProductTypeEnum.lesa.name:
                "Леса"
                # ProductSizeEnum.katta.name: "Большая Леса",
                # ProductSizeEnum.orta.name: "Средняя Леса",
                # ProductSizeEnum.kichik.name: "Маленькая Леса",
            ,

            ProductTypeEnum.monolit.name: "Монолитная стойка",
            ProductTypeEnum.taxta_opalubka.name: {
                ProductSizeEnum.four_meters.name: "4-метровая деревянная доска",
                ProductSizeEnum.three_meters.name: "3-метровая деревянная доска",
                ProductSizeEnum.two_meters.name: "2-метровая деревянная доска",
                ProductSizeEnum.one_meter.name: "Деревянная доска длиной 1 метр",
            },
            ProductTypeEnum.metal_opalubka.name: "3-метровый металлический настил"
        },
    }

    SELECT_INVALID_PRODUCT = {
        LanguageEnum.uzl.name: "Iltimos, quyidan kerakli mahsulotni birini tanlang!",
        LanguageEnum.uzk.name: "Илтимос, қуйидан керакли маҳсулотни бирини танланг!",
        LanguageEnum.rus.name: "Пожалуйста, выберите нужный вам товар ниже!",
    }

    INSERT_QUANTITY_PRODUCT = {
        LanguageEnum.uzl.name: "Kerakli miqdorni kiriting: ⬇️",
        LanguageEnum.uzk.name: "Керакли миқдорни киритинг: ⬇️",
        LanguageEnum.rus.name: "Введите необходимое количество: ⬇️",
    }

    LESA_SIZE_TRANSLATION = {
        "uzl": {
            ProductSizeEnum.katta.name: "Katta",
            ProductSizeEnum.orta.name: "O'rta",
            ProductSizeEnum.kichik.name: "Kichik",
        },
        "uzk": {
            ProductSizeEnum.katta.name: "Катта",
            ProductSizeEnum.orta.name: "Ўрта",
            ProductSizeEnum.kichik.name: "Кичик",
        },
        "rus": {
            ProductSizeEnum.katta.name: "Большой",
            ProductSizeEnum.orta.name: "Середина",
            ProductSizeEnum.kichik.name: "Маленький",
        }
    }

    INSERT_INVALID_SIZE = {
        "uzl": "Iltimos, quyidan kerakli hajmni tanlang!",
        "uzk": "Илтимос, қуйидан керакли ҳажмни танланг!",
        "rus": "Пожалуйста, выберите необходимый размер ниже!",
    }

    CHOOSE_ANOTHER_PRODUCT = {
        "uzl": "Yana qo'shmoqchi bo'lgan mahsulotingizni belgilang: \n\n",
        "uzk": "Яна қўшмоқчи бўлган маҳсулотингизни белгиланг: \n\n",
        "rus": "Выберите товар, который хотите добавить: \n\n",
    }

    YES_NO_TEXT = {
        "uzl": {"yes": "Ha", "no": "Yo‘q"},
        "uzk": {"yes": "Ха", "no": "Йўқ"},
        "rus": {"yes": "Да", "no": "Нет"},
    }

    ASK_RENTER_FULLNAME = {
        "uzl": "Yaxshi, endi navbatda, ijaraga oluvchining ism va familiyasini kiriting(masalan, Ali Valiyev): ",
        "uzk": "Яхши, энди навбатда, ижарага олувчининг исм ва фамилиясини киритинг(масалан, Али Валиев):",
        "rus": "Хорошо, теперь введите имя и фамилию арендатора (например, Али Валиев):",
    }

    INVALID_YES_NO = {
        "uzl": "Iltimos, javobingizni quyidagi tugmalar orqali bering⬇️",
        "uzk": "Илтимос, жавобингизни қуйидаги тугмалар орқали беринг⬇️",
        "rus": "Пожалуйста, ответьте, используя кнопки ниже⬇️",
    }

    GET_RENT_START_DATE = {
        "uzl": "Ijarani boshlanish sanasini kiriting <b>(DD.MM.YYYY)</b>: ",
        "uzk": "Ижарани бошланиш санасини киритинг <b>(ДД.ММ.ЙЙЙЙ)</b>: ",
        "rus": "Введите дату начала аренды <b>(ДД.ММ.ГГГГ)</b>:",
    }

    GET_RENT_END_DATE = {
        "uzl": "Ijarani tugash sanasini ham kiriting <b>(DD.MM.YYYY)</b>: ",
        "uzk": "Ижарани тугаш санасини ҳам киритинг <b>(ДД.ММ.ЙЙЙЙ)</b>: ",
        "rus": "Также укажите дату окончания аренды <b>(ДД.ММ.ГГГГ)</b>: ",
    }

    ASK_LOCATION_TYPE = {
        "uzl": "Joylashuvni qaysi ko'rinishda yuborasiz?",
        "uzk": "Жойлашувни қайси кўринишда юборасиз?",
        "rus": "В каком формате вы отправляете местоположение?",
    }

    LOCATION_INVALID = {
        "uzl": "Joylashuvni yuborish turini tugmalar orqali belgilang⬇️",
        "uzk": "Жойлашувни юбориш турини тугмалар орқали белгиланг⬇️",
        "rus": "Укажите тип отправки по местоположению с помощью кнопок.⬇️",
    }

    # LOCATION_KB_TRANSLATION = {
    #     "uzl": {
    #         LocationTypeEnum.map.name: "Xarita📍",
    #         LocationTypeEnum.text.name: "Matn📝",
    #     },
    #     "uzk": {
    #         LocationTypeEnum.map.name: "Харита📍",
    #         LocationTypeEnum.text.name: "Матн📝",
    #     },
    #     "rus": {
    #         LocationTypeEnum.map.name: "Карта📍",
    #         LocationTypeEnum.text.name: "Текст📝",
    #     },
    # }

    LOCATION_REQUEST = {
        "uzl": "Mijozning joylashuvini yuboring📍 \n"
               "(Joylashuv sizga yuborilgan bo'lsa, uni botga jo'nating.) ",
        "uzk": "Мижознинг жойлашувини юборинг📍\n"
               "(Жойлашув сизга юборилган бўлса, уни ботга жўнатинг.)",
        "rus": "Отправить местоположение клиента📍\n"
               "(Если вам были отправлены данные о местоположении, отправьте их боту.)",
    }

    SENT_LOCATION_INFO = {
        "uzl":
            "📍<b>Lokatsiya qabul qilindi</b>\n\n"
            # "<b>Latitude</b>: <u>{renter_latitude}</u>\n"
            # "<b>Longitude</b>: <u>{renter_longitude}</u>\n"
            "<b>Masofa</b>: <u>{distance_km}</u> km\n\n"
            "<b>Yetkazib berish narxi</b>:\n"
            "<b>2.5 km radius uchun: </b>\n"
            "\n    <b>Yetkazib berish:</b> <u>30.000</u> so'm\n"
            "\n    <b>Qayta olib kelish:</b> <u>30.000</u> so'm\n"
            "\n    <b>Umumiy:</b> <u>60.000</u> so'm\n\n"
            "<b>Kiritilgan joylashuv uchun</b>: <u>{price_delivery}</u> so'm",

        "uzk":
            "<b>📍Локация қабул қилинди</b>\n\n"
            # "<b>Латитуде</b>: <u>{renter_latitude}</u>\n"
            # "<b>Лонгитуде</b>: <u>{renter_longitude}</u>\n"
            "<b>Масофа</b>: <u>{distance_km}</u> км\n\n"
            "<b>Етказиб бериш нархи</b>:\n"
            "<b>2.5 км радиус учун: </b>\n"
            "\n    <b>Етказиб бериш:</b> <u>30.000</u> сўм\n"
            "\n    <b>Қайта олиб келиш:</b> <u>30.000</u> сўм\n"
            "\n    <b>Умумий:</b> <u>60.000</u> сўм\n\n"
            "<b>Киритилган жойлашув учун</b>: <u>{price_delivery}</u> сўм",

        "rus":
            "📍<b>Принятое местоположение</b>\n\n"
            # "<b>Широта</b>: <u>{renter_latitude}</u>\n"
            # "<b>Долгота</b>: <u>{renter_longitude}</u>\n"
            "<b>Расстояние</b>: <u>{distance_km}</u> км\n\n"
            "<b>Стоимость доставки</b>:\n"
            "<b>В радиусе 2,5 км:</b>\n"
            "\n    <b>Доставка:</b> <u>30 000</u> сумов\n"
            "\n    <b>Возврат:</b> <u>30 000</u> сумов\n"
            "\n    <b>Итого:</b> <u>60 000</u> сумов\n\n"
            "<b>Для указанного местоположения:</b> <u>{price_delivery}</u> сум",
    }

    DATE_MODE_ASK = {
        "uzl": "Ijara sanasini qanday kiritamiz?\n\n1) Boshlanish + tugash (aniq sanali)\n2) Faqat boshlanish (qaytganda tugaydi)",
        "uzk": "Ижара санасини қандай киритамиз?\n\n1) Бошланиш + тугаш (аниқ санали)\n2) Фақат бошланиш (қайтарганда тугайди)",
        "rus": "Как вводим даты аренды?\n\n1) Начало + конец (фиксированно)\n2) Только начало (закроем при возврате)"
    }

    DATE_MODE_FIXED = {
        "uzl": "Boshlanish + tugash",
        "uzk": "Бошланиш + тугаш",
        "rus": "Начало + конец"
    }

    DATE_MODE_OPEN = {
        "uzl": "Faqat boshlanish (qaytganda tugaydi)",
        "uzk": "Фақат бошланиш (қайтарганда тугайди)",
        "rus": "Только начало (закроем при возврате)"
    }

    DATE_MODE_INVALID = {
        "uzl": "Iltimos, faqat tugmalar orqali tanlang.",
        "uzk": "Илтимос, фақат тугмалар орқали танланг.",
        "rus": "Пожалуйста, выберите только кнопкой."
    }
