#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import telebot

from telebot import types, apihelper

from src.models import User, GirlsFilter, ExtendedGirlsFilter, session
from src.extra import utils, API_TOKEN, AVAILABLE_COUNTRIES_LIST, PROMOCODES
from src.extra.text import *


apihelper.proxy = {'https':'socks5h://127.0.0.1:9050'}
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def process_welcome_step(message):
    welcome = MSG_WELCOME.format(message.from_user.username)
    keyboard = utils.create_inline_keyboard(*AVAILABLE_COUNTRIES_LIST, row_width=1)

    bot.send_message(message.chat.id, welcome, parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, MSG_ENTER_COUNTRY, reply_markup=keyboard)


def process_city_step(message):
    city = message.text.capitalize()

    if city in AVAILABLE_CITIES_LIST:
        bot.send_message(message.chat.id, MSG_MENU_ATTENTION, reply_markup=KB_MENU)
    elif message.text == '/reset':
        msg = bot.send_message(message.chat.id, MSG_RESET)
        bot.register_next_step_handler(msg, process_welcome_step)
    else:
        msg = bot.send_message(message.chat.id, MSG_UNAVAILABLE_CITY)
        bot.register_next_step_handler(msg, process_city_step)


def process_promocode_step(message):
    promocode = message.text
    if promocode in PROMOCODES.values():
        bot.send_message(message.chat.id, MSG_SUCCESS_PROMO, reply_markup=KB_MENU)
    elif promocode.endswith('Отмена'):
        bot.send_message(message.chat.id, MSG_CANCELED, reply_markup=KB_MENU)
    else:
        msg = bot.send_message(message.chat.id, MSG_ERROR_PROMO, reply_markup=KB_CANCEL)
        bot.register_next_step_handler(msg, process_promocode_step)


@bot.message_handler(regexp='Каталог')
def catalog(message):
    print(000, message.text)


@bot.message_handler(regexp='Фильтры')
def filters(message):
    print(000, message.text)


@bot.message_handler(regexp='Гарантии|О сервисе')
def about(message):
    abouts = {'Гарантии': MSG_GUARANTY, 'О сервисе': MSG_ABOUT_SERVICE}
    about_text = abouts.get(' '.join(message.text.split()[1:]))
    bot.send_message(message.chat.id, about_text)


@bot.message_handler(regexp='Скидки')
def discounts(message):
    bot.send_message(message.chat.id, MSG_DISCOUNTS, reply_markup=KB_PROMOCODE)


@bot.message_handler(regexp='Статистика')
def statistic(message):
    bot.send_message(message.chat.id, MSG_STATISTIC)


class CallbackQuery:
    @staticmethod
    def cb_countries(chat_id):
        msg = bot.send_message(chat_id, MSG_ENTER_CITY)
        bot.register_next_step_handler(msg, process_city_step)

    @staticmethod
    def cb_promocode(chat_id, message_id):
        msg = bot.edit_message_text(MSG_ENTER_PROMO, chat_id, message_id)
        bot.register_next_step_handler(msg, process_promocode_step)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    cb_text = call.message.json['reply_markup']['inline_keyboard'][0][0]['text']

    if cb_text in AVAILABLE_COUNTRIES_LIST:
        CallbackQuery.cb_countries(call.message.chat.id)
    elif 'PROMOCODE' in cb_text:
        CallbackQuery.cb_promocode(call.message.chat.id, call.message.message_id)


def main_loop():
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.polling()


if __name__ == '__main__':
    main_loop()
