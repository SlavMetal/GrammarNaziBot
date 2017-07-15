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

# TODO add strings support
# TODO add languages selection
# TODO bold highlightning
# TODO available only for one group and admins
# because of API limits

import logging
import requests
import yaml
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Open the config.yml file
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text('Хой!')


def help(bot, update):
    update.message.reply_text('Help!')


def echo(bot, update):
    url = "http://speller.yandex.net/services/spellservice.json/checkText?text="
    respond = requests.get(url + update.message.text)  # Get JSON data
    json_data = respond.json()  # Parsed JSON data

    corrected_words = ''  # Put corrected words here

    for i in json_data:  # Add corrected words in array
        arr = i['s']
        if len(arr) == 1:
            corrected_words += arr[0] + '; '
        else:
            brackets = ''
            for j in range(1, len(arr)):
                brackets += arr[j]
                if j+1 != len(arr):  # Check if the element is not the last one
                    brackets += ', '
            corrected_words += arr[0] + ' (' + brackets + '?); '
    update.message.reply_text(corrected_words, reply_to_message_id=update.message.message_id)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(cfg['botapi_token'])
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()