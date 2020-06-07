# -*- coding: utf-8 -*-
from sqlalchemy import or_
from sqlalchemy.orm import subqueryload
from sqlalchemy.sql.sqltypes import VARCHAR
from sqlalchemy.dialects.postgresql.base import ENUM
from sqlalchemy.dialects.postgresql.array import ARRAY

from src.messages import *
from src.models import User, user_session, Girl, girl_session, UserGirlBaseFilter, UserGirlExtFilter, \
    UserGirlServices, GirlBaseFilter, GirlExtFilter

from src.core.helpers.types import KeyboardOption
from src.core.common import bot
from src.core.helpers.botutils import BotUtils


OFFSET_STATE = {}


def create_main_catalog_keyboard(catalog_profiles_num):
    buttons = (
        (f'⚙️ ПОКАЗЫВАТЬ ПО   -   {catalog_profiles_num}', f'{PX_CAT_SET}profiles_num'),
        ('👠 ПОКАЗАТЬ АНКЕТЫ', f'{PX_CAT}{catalog_profiles_num}')
    )
    options = (KeyboardOption(name=name, callback=callback) for name, callback in buttons)
    return Keyboards.create_inline_keyboard_ext(*options, prefix='', row_width=1)


def set_catalog_profiles_limit(username, chat_id, message_id, new_val):
    def is_valid(val):
        return (val == 1 or val % 5 == 0) and val != 0

    if new_val:
        user = user_session.query(User).filter_by(username=username).one()
        BotUtils.write_changes(user, 'catalog_profiles_num', new_val)

        kb = create_main_catalog_keyboard(user.catalog_profiles_num)
        bot.edit_message_text(MSG_CATALOG, chat_id, message_id, parse_mode='Markdown', reply_markup=kb)
        bot.send_message(chat_id, MSG_SUCCESS_CHANGE_OPTION, parse_mode='Markdown')
    else:
        options = (KeyboardOption(name=f'{x}', callback=f'{PX_CAT_SET}profiles_num:{x}') for x in range(11) if is_valid(x))
        kb = Keyboards.create_inline_keyboard_ext(*options, prefix='', row_width=1)
        bot.edit_message_text(MSG_CATALOG_NUM_PROFILES, chat_id, message_id, parse_mode='Markdown', reply_markup=kb)


class CatalogBase:
    __slots__ = ('_username', '_chat_id', '_message_id')

    def __init__(self, **kwargs):
        self._username      = kwargs['username']
        self._chat_id       = kwargs['chat_id']
        self._message_id    = kwargs.get('message_id', None)


class CatPaymentDetail(CatalogBase):
    __slots__ = ('_girl_id', )

    def __init__(self, girl_id, **kwargs):
        super().__init__(**kwargs)
        self._girl_id = girl_id

    def send_payment_details(self):
        pass


class CatPayment(CatalogBase):
    __slots__ = ('_girl_id', )

    def __init__(self, girl_id, **kwargs):
        super().__init__(**kwargs)
        self._girl_id = girl_id

    def send_payment(self):
        pass


class CatProfileDetail(CatalogBase):
    __slots__ = ('_girl_id', )

    def __init__(self, girl_id, **kwargs):
        super().__init__(**kwargs)
        self._girl_id = girl_id

    def send_profile_detail(self):
        pass


class _GirlsSelectionMixin(CatalogBase):
    __slots__ = ('_profiles_limit', '_more_profiles', '_order_by')

    _default_enum_value = 'Не важно'
    _exclude_columns_names = ('country', )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._profiles_limit    = kwargs.get('profiles_limit')
        self._order_by          = kwargs.get('order_by', GirlBaseFilter.price)
        self._more_profiles     = kwargs.get('increment', False)

    @property
    def _slice_range(self):
        if self._more_profiles:
            offset = OFFSET_STATE.get(self._chat_id, 0)
            end = offset + self._profiles_limit
        else:
            offset = 0
            end = offset + self._profiles_limit

        OFFSET_STATE[self._chat_id] = end
        return offset, end

    @staticmethod
    def _get_services_items(user_services_instance):
        return dict(filter(
            lambda elem: elem[1] is True, user_services_instance.items()
        ))

    def _get_sql_condition(self, table, key, val, type_, nullable):
        t_key = table.c[key]

        if type_ == VARCHAR:
            return t_key == val

        if type_ == ENUM and val.value != self._default_enum_value:
            return t_key == val.value

        if type_ == ARRAY and val:
            if nullable:
                return or_(t_key.is_(None), t_key.in_(range(*val)))
            else:
                return t_key.in_(range(*val))

    def _get_filter_items(self, girl_filter_class, user_filter_instance):
        table = girl_filter_class.__table__
        ufi = user_filter_instance
        return filter(
            lambda x: x is not None,
            (
                self._get_sql_condition(table, key, val, type_, nullable)
                for key, _, val, type_, nullable in ufi.as_tuple(ufi, format_value=False)
                if key not in self._exclude_columns_names
            )
        )

    def _get_user_filters_instances(self):
        return user_session.\
            query(UserGirlBaseFilter, UserGirlExtFilter, UserGirlServices).\
            filter_by(user_username=self._username).one()

    def get_girls(self):
        # NOTE: попробовать в query подгружать только определенные поля у relationships
        user_base_filter, user_ext_filter, user_services = self._get_user_filters_instances()

        user_base_filter_items = self._get_filter_items(GirlBaseFilter, user_base_filter)
        user_ext_filter_items = self._get_filter_items(GirlExtFilter, user_ext_filter)
        user_services_items = self._get_services_items(user_services.as_dict(user_services, only_key_val=True))

        return girl_session. \
            query(Girl). \
            join(Girl.base_filter).options(subqueryload(Girl.base_filter)). \
            filter(
                GirlBaseFilter.country == user_base_filter.country.split(' ')[-1],
                *user_base_filter_items
            ). \
            join(Girl.ext_filter).options(subqueryload(Girl.ext_filter)). \
            filter(*user_ext_filter_items). \
            join(Girl.services).options(subqueryload(Girl.services)). \
            filter_by(**user_services_items). \
            order_by(self._order_by). \
            slice(*self._slice_range). \
            values(Girl.id, Girl.name, GirlBaseFilter.age, GirlBaseFilter.price, Girl.preview_photo)


class CatProfiles(_GirlsSelectionMixin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_profiles(self):
        girls = self.get_girls()

        for g in girls:
            print(g)
