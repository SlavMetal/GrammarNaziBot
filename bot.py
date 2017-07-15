#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 SlavMetal <7tc@protonmail.com>
#
# This file is part of GrammarNaziBot.
#
# GrammarNaziBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GrammarNaziBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GrammarNaziBot.  If not, see <http://www.gnu.org/licenses/>.

# TODO bold highlighting
# TODO rewrite code of sending corrected words
# TODO Functions for checks

import logging
import requests
import yaml
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import wraps

# Open the config.yml file
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Functions with this decorator will work only in PM
def private(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        if update.message.chat.type != 'private':
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


@private
def start(bot, update):
    update.message.reply_text('Hello there, {}! You can use me right here or add me to groups as well. '
                              'I\'m actually private bot, see /help for more details. '
                              .format(update.message.from_user.first_name))


@private
def help(bot, update):
    update.message.reply_text('This bot checks grammar of every message sent in PM or group and '
                              'it automatically detects English, Russian and Ukrainian words. '
                              'Because of API limitations, this bot will NOT work for you or your groups, '
                              'but you can use the source code to build your own `Grammar Nazi Bot`!\n\n'
                              'Source code: https://github.com/SlavMetal/GrammarNaziBot\n'
                              'Author: @SlavMetal', disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)


def echo(bot, update):
    url = "http://speller.yandex.net/services/spellservice.json/checkText?text=" + update.message.text
    respond = requests.get(url)  # Get JSON data
    json_data = respond.json()  # Parsed JSON data

    corrected_words = ''  # Put corrected words here
    chat = update.message.chat.id
    word_entries = 0
    current_entry = 0

    for i in json_data:  # Counts corrected words (w/o possible options)
        if i['s']:
            word_entries += 1

    if len(json_data) > 0 and chat in cfg['admins_ids'] or chat in cfg['groups_ids']:
        for i in json_data:  # Adding corrected words to string
            arr = i['s']  # Get corrected words in 'i' iteration
            arr_length = len(arr)
            if arr_length == 1:
                corrected_words += arr[0]
            elif arr_length > 1:  # If there are other possible corrected words
                brackets = ''
                for j in range(1, arr_length):
                    brackets += arr[j]
                    if not is_last(j, arr_length):
                        brackets += ', '
                corrected_words += arr[0] + ' ({}?)'.format(brackets)
            corrected_words += '; ' if current_entry < word_entries - 1 else '.'
            current_entry += 1
        update.message.reply_text(corrected_words, reply_to_message_id=update.message.message_id)


def is_last(index: int, length: int):
    if index + 1 != length:
        return False
    return True


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(cfg['botapi_token'])
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on no command
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
