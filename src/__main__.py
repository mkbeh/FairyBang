#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#       CREATED BY:  "L"
#       MY MAIL:     llawlietorigin@gmail.com
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


import ssl

from aiohttp import web
from loguru import logger

from src import SUPPORT_MAIL, DEBUG, WEBHOOK_PORT, WEBHOOK_LISTEN, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV, \
    WEBHOOK_URL_BASE, WEBHOOK_URL_PATH
from src.models import User
from src.messages import *

from src.core.common import bot, app
from src.core.stepsprocesses import process_change_country_step
from src.core.helpers import pyutils
from src.core.helpers.botutils import BotUtils

from src.core.callbackqueries.common import MainCBQ, FiltersCBQ, FiltersOptionsHandler, \
    create_main_catalog_keyboard, set_catalog_profiles_limit, CatProfiles, CatProfileDetail, CatPayment, \
    CatPaymentDetail, get_total_profiles


@bot.message_handler(regexp='Каталог')
def catalog(message):
    user_id, username, chat_id, message_id, msg_text = BotUtils.get_message_data(message)
    catalog_profiles_num = BotUtils.get_obj(User, {'id': user_id}).catalog_profiles_num

    kb = create_main_catalog_keyboard(catalog_profiles_num)
    bot.send_message(chat_id, MSG_CATALOG.format(get_total_profiles()), parse_mode='Markdown', reply_markup=kb)


@bot.message_handler(regexp='Фильтры')
def filters(message):
    bot.send_message(message.chat.id, MSG_FILTERS, parse_mode='Markdown', reply_markup=KB_FILTERS_MENU)


@bot.message_handler(regexp='Гарантии|О сервисе')
def about(message):
    abouts = {'Гарантии': MSG_GUARANTY, 'О сервисе': MSG_ABOUT_SERVICE.format(SUPPORT_MAIL)}
    about_text = abouts.get(' '.join(message.text.split()[1:]))
    bot.send_message(message.chat.id, about_text, parse_mode='Markdown')


@bot.message_handler(regexp='Скидки')
def discounts(message):
    user_id, username, chat_id, message_id, msg_text = BotUtils.get_message_data(message)
    user = BotUtils.get_user(user_id, username)
    if user.promocode:
        text = MSG_DISCOUNTS.format(user.promocode, str(user.promo_discount) + ' %', user.discount_expires_days)
    else:
        text = MSG_DISCOUNTS.format('не введен', 'отсутствует', 0)

    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=KB_PROMOCODE)


@bot.message_handler(regexp='Статистика')
def statistic(message):
    user_id, username, chat_id, message_id, msg_text = BotUtils.get_message_data(message)
    user = BotUtils.get_user(user_id, username)
    msg = MSG_STATISTIC.format(
        bot_active_days=0,
        total_ordered_girls=0,
        bot_total_money=0,

        days_since_register=user.days_since_register,
        total_txs=user.total_txs,
        total_qiwi_sum=int(user.total_qiwi_sum),
        total_girls=user.total_girls,
        total_girls_profiles=get_total_profiles(),
    )
    bot.send_message(chat_id, msg, parse_mode='Markdown')


def main_callback_query(call):
    user_id, username, chat_id, message_id, msg_text = BotUtils.get_message_data(call, callback=True)

    if re.search(PN_SET, msg_text):
        country = msg_text.split(':')[-1]
        process_change_country_step(country, user_id, username, chat_id)

    elif re.search(PN_ENTER, msg_text):
        MainCBQ.enter_promocode(chat_id)


def catalog_callback_query(call):
    # TODO: начать просмотр девушек с N девушки (offset от юзверя)
    user_id, username, chat_id, message_id, msg_text = BotUtils.get_message_data(call, callback=True)
    default_args = (user_id, username, chat_id, message_id)
    default_kwargs = {'user_id': user_id, 'username': username, 'chat_id': chat_id, 'message_id': message_id}

    if re.search(PN_CAT_SET, msg_text):
        try:
            new_val = msg_text.split(':')[2]
        except IndexError:
            new_val = None

        set_catalog_profiles_limit(*default_args, new_val)

    elif re.match(PN_CAT, msg_text):
        profiles_limit = msg_text.split(':')[1]
        CatProfiles(profiles_limit=profiles_limit, **default_kwargs).send_profiles()

    elif re.match(PN_CAT_MORE, msg_text):
        profiles_limit = msg_text.split(':')[1]
        CatProfiles(profiles_limit=profiles_limit, more=True, **default_kwargs).send_profiles()

    elif re.match(PN_CAT_PROFILE, msg_text):
        profiles_limit, girl_id, last_profile = msg_text.split(':')[1:]
        kwargs = {'girl_id': girl_id, 'last_profile': last_profile, 'profiles_limit': profiles_limit}
        CatProfileDetail(**kwargs, **default_kwargs).send_profile_detail()

    elif re.match(PN_CAT_PAY_BACK, msg_text):
        pass

    elif re.match(PN_CAT_PAY, msg_text):
        profiles_limit, girl_id, last_profile = msg_text.split(':')[1:]
        kwargs = {'girl_id': girl_id, 'last_profile': last_profile, 'profiles_limit': profiles_limit}
        CatPayment(**kwargs, **default_kwargs).send_payment()


def filters_callback_query(call):
    user_id, username, chat_id, message_id, msg_text = BotUtils.get_message_data(call, callback=True)
    default_kwargs = {'user_id': user_id, 'username': username, 'chat_id': chat_id, 'message_id': message_id}

    if re.match(PN_FIL, msg_text) or re.match(PN_CH_BACK, msg_text):
        filter_name = msg_text.split(':')[1]
        FiltersCBQ(filter_name, *default_kwargs.values()).send_options()
        return

    elif re.match(PN_FIL_OP, msg_text):
        filter_name, option_key = msg_text.split(':')[1:]
        kwargs = {'filter_name': filter_name, 'option_name_key': option_key}
        kwargs.update(default_kwargs)
        FiltersOptionsHandler(**kwargs).send_change_option_value_msg()
        return

    elif re.match(PN_FIL_MOVE, msg_text):
        filter_name, move_where = msg_text.split(':')[1:]
        increment = 1 if move_where == 'next' else -1
        FiltersCBQ(filter_name, *default_kwargs.values(), increment=increment).send_options()

    elif re.match(PN_FIL_ENTER, msg_text):
        country = msg_text.split(':')[-1]
        FiltersOptionsHandler.change_country_option_value(country, user_id, chat_id)

    elif re.match(PN_CH_SET, msg_text):
        filter_name, option_key, option_value = msg_text.split(':')[1:]
        FiltersOptionsHandler.change_enum_option_value(filter_name, option_key, option_value, *default_kwargs.values())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    msg_text = BotUtils.get_message_data(call, callback=True)[-1]
    call.data = pyutils.remove_prefix(call.data)

    if DEBUG:
        logger.info(f'--- CALLBACK DATA --- {msg_text}')

    try:
        if msg_text.startswith('MAIN'):
            main_callback_query(call)

        if msg_text.startswith('CAT'):
            catalog_callback_query(call)

        if msg_text.startswith('FIL') or msg_text.startswith('CH'):
            filters_callback_query(call)
    except:
        # todo: if exception is blocked bot by user - add user to block too and unblock when he restart the bot.
        logger.exception('CALLBACK QUERY ERRORS')


def main_loop():
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()

    if DEBUG:
        bot.polling()
    else:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                        certificate=open(WEBHOOK_SSL_CERT, 'r'))

        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

        web.run_app(
            app,
            host=WEBHOOK_LISTEN,
            port=WEBHOOK_PORT,
            ssl_context=context,
        )


if __name__ == '__main__':
    main_loop()
