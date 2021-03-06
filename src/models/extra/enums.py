# -*- coding: utf-8 -*-
import enum


# --- Extended girls filter enums ---
class ExtCategory(enum.Enum):
    not_important   = 'Не важно'

    individuals     = 'Индивидуалки'
    masseuses       = 'Массажистки'
    elite           = 'Элитные'


class ExtHairColor(enum.Enum):
    not_important = 'Не важно'

    blonde        = 'Блондинки'
    brunnete      = 'Брюнетки'
    brown         = 'Шатенки'
    red           = 'Рыжие'
    light_brown   = 'Русые'


class ExtBodyType(enum.Enum):
    not_important   = 'Не важно'

    slim            = 'Стройное'
    athletic        = 'Атлетическое'
    average         = 'Среднее'
    plump           = 'Полное'
    thin            = 'Худощавое'


class ExtSkinColor(enum.Enum):
    not_important   = 'Не важно'

    pale            = 'Бледный'
    dark            = 'Смуглый'
    sunburnt        = 'Загорелый'
    brown           = 'Коричневый'
    black           = 'Черный'


class ExtNationality(enum.Enum):
    not_important = 'Не важно'

    ru = 'Русские'
    uc = 'Украинки'
    uz = 'Узбечки'
    td = 'Таджички'
    ar = 'Армянки'
    az = 'Азиатки'
    ng = 'Негритянки'


class ExtSmoking(enum.Enum):
    not_important   = 'Не важно'

    smoking         = 'Курящие'
    no_smoking      = 'Не курящие'


class ExtGirlFriends(enum.Enum):
    not_important   = 'Не важно'

    exist           = 'Есть подружки'
    no_exist        = 'Без подруг'


ENUMS = {
    'category'      : ExtCategory,
    'hair_color'    : ExtHairColor,
    'body_type'     : ExtBodyType,
    'skin_color'    : ExtSkinColor,
    'nationality'   : ExtNationality,
    'smoking'       : ExtSmoking,
    'girl_friends'  : ExtGirlFriends,
}
