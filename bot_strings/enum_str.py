from utils.enums import ProductSizeEnum, ProductTypeEnum

SIZE_LABEL = {
    "uzl": {
        ProductSizeEnum.katta: "Katta",
        ProductSizeEnum.orta: "O'rta",
        ProductSizeEnum.kichik: "Kichik",
        ProductSizeEnum.four_meters: "4 metrlik",
        ProductSizeEnum.three_meters: "3 metrlik",
        ProductSizeEnum.two_meters: "2 metrlik",
        ProductSizeEnum.one_meter: "1 metrlik",
    },
    "uzk": {
        ProductSizeEnum.katta: "Катта",
        ProductSizeEnum.orta: "Ўрта",
        ProductSizeEnum.kichik: "Кичик",
        ProductSizeEnum.four_meters: "4 метрлик",
        ProductSizeEnum.three_meters: "3 метрлик",
        ProductSizeEnum.two_meters: "2 метрлик",
        ProductSizeEnum.one_meter: "1 метрлик",
    },
    "rus": {
        ProductSizeEnum.katta: "Большой",
        ProductSizeEnum.orta: "Середина",
        ProductSizeEnum.kichik: "Маленький",
        ProductSizeEnum.four_meters: "4 метра",
        ProductSizeEnum.three_meters: "3 метра",
        ProductSizeEnum.two_meters: "2 метра",
        ProductSizeEnum.one_meter: "1 метр",
    }
}

PRODUCT_TYPE_LABEL = {
    "uzl": {
        ProductTypeEnum.lesa: "Lesa",
        ProductTypeEnum.monolit: "Monolit ustun",
        ProductTypeEnum.taxta_opalubka: "Taxta Opalubka",
        ProductTypeEnum.metal_opalubka: "Metal Opalubka",
    },
    "uzk": {
        ProductTypeEnum.lesa: "Леса",
        ProductTypeEnum.monolit: "Монолит устун",
        ProductTypeEnum.taxta_opalubka: "Тахта опалубка",
        ProductTypeEnum.metal_opalubka: "Метал Опалубка",
    },
    "rus": {
        ProductTypeEnum.lesa: "Леса",
        ProductTypeEnum.monolit: "Монолитная стойка",
        ProductTypeEnum.taxta_opalubka: "Дощатая опалубка",
        ProductTypeEnum.metal_opalubka: "Металлическая опалубка",
    }
}
