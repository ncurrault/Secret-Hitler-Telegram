# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import Secret_Hitler
import telegram
from telegram.ext import Updater, CommandHandler, Filters

from telegram.error import TelegramError
import logging

import sys
import os

with open("ignore/API_key.txt", "r") as f:
    API_KEY = f.read().rstrip()

bot = telegram.Bot(token=API_KEY)

def get_static_handler(command):
    """
    Given a string command, returns a CommandHandler for that string that
    responds to messages with the content of static_responses/[command].txt

    Throws IOError if file does not exist or something
    """

    f = open("static_responses/{}.txt".format(command), "r")
    response = f.read()

    return CommandHandler(command, \
        ( lambda bot, update : \
        bot.send_message(chat_id=update.message.chat.id, text=response) ) )

def newgame_handler(bot, update):
    """
    Create a new game (if doing so would overwrite an existing game in progress, only proceed if message contains "confirm")
    """
    global game # TODO: allow multiple games across different chats
    chat_id = update.message.chat.id
    if game is not None and game.game_state != Secret_Hitler.GameStates.GAME_OVER and update.message.text.find("confirm") == -1:
        bot.send_message(chat_id=chat_id, text="Warning: game already in progress here. Reply '/newgame confirm' to confirm")
    else:
        game = Secret_Hitler.Game(chat_id)
        bot.send_message(chat_id=chat_id, text="Created game! /joingame to join, /startgame to start")

def parse_message(msg):
    """
    Helper function: split a messsage into its command and its arguments (two strings)
    """
    command = msg.split()[0]
    if command.endswith(bot.username):
        command = command[1:command.find("@")]
    else:
        command = command[1:]
    args = msg.split()[1:]
    if len(args) == 0:
        args = "" #None
    else:
        args = " ".join(args)
    return command, args

COMMAND_ALIASES = {"nom": "nominate", "blam": "blame"}
def game_command_handler(bot, update):
    """
    Pass all commands that Secret_Hitler.Game can handle to game's handle_message method
    Send outputs as replies via Telegram
    """
    command, args = parse_message(update.message.text)
    if command in COMMAND_ALIASES.keys():
        command = COMMAND_ALIASES[command]
    player_id, chat_id = update.message.from_user.id, update.message.chat.id

    global game
    if game is None:
        bot.send_message(chat_id=chat_id, text="Error: no game in progress here")
    else:
        player = game.get_player_by_id(player_id)
        if not player: # player's first message can set their nickname
            if args and (game.check_name(args) is None): # args is a valid name
                player = Secret_Hitler.Player(player_id, args)
            else:
                # TODO: maybe also chack their Telegram first name
                player = Secret_Hitler.Player(player_id, update.message.from_user.first_name)

        # use player object from game if it exists

        try:
            reply = game.handle_message(player, command, args)

            # pass all supressed errors (if any) directly to the handler in
            # the order that they occurred
            while len(Secret_Hitler.telegram_errors) > 0:
                handle_error(bot, update, Secret_Hitler.telegram_errors.pop(0))
            # TODO: it would be cleaner to just have a consumer thread handling
            # these errors as they occur

            if reply: # reply is None if no response is necessary
                if command in Secret_Hitler.Game.MARKDOWN_COMMANDS: # these require links/tagging
                    bot.send_message(chat_id=chat_id, text=reply, parse_mode=telegram.ParseMode.MARKDOWN)
                else:
                    bot.send_message(chat_id=chat_id, text=reply)

        except Secret_Hitler.GameOverException:
            return

# Credit (TODO: actual attribution): https://github.com/CaKEandLies/Telegram_Cthulhu/blob/master/cthulhu_game_bot.py#L63
def feedback_handler(bot, update, args=None):
    """
    Store feedback from users in a text file.
    """
    if args and len(args) > 0:
        feedback = open("ignore/feedback.txt", "a")
        feedback.write("\n")
        feedback.write(update.message.from_user.first_name)
        feedback.write("\n")
        # Records User ID so that if feature is implemented, can message them
        # about it.
        feedback.write(str(update.message.from_user.id))
        feedback.write("\n")
        feedback.write(" ".join(args))
        feedback.write("\n")
        feedback.close()
        bot.send_message(chat_id=update.message.chat_id,
                         text="Thanks for the feedback!")
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Format: /feedback [feedback]")

def handle_error(bot, update, error):
    try:
        raise error
    except TelegramError:
        logging.getLogger(__name__).warning('TelegramError! %s caused by this update: %s', error, update)

def save_game(bot, update):
    if game is not None:
        fname = "ignore/aborted_game.p"
        i = 0
        while os.path.exists(fname):
            fname = "ignore/aborted_game_{}.p".format(i)
            i += 1 # ensures multiple games can be saved

        game.save(fname)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Saved game in current state as '{}'".format(fname))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        game = Secret_Hitler.Game.load(sys.argv[1])
    else:
        game = None

    # Set up all command handlers

    updater = Updater(token=API_KEY) # TODO init with bot=bot -> spooky errors?
    dispatcher = updater.dispatcher

    dispatcher.add_handler(get_static_handler("start"))
    dispatcher.add_handler(get_static_handler("help"))
    dispatcher.add_handler(get_static_handler("changelog"))
    dispatcher.add_handler(CommandHandler('feedback', feedback_handler, pass_args=True))

    # memes
    dispatcher.add_handler(CommandHandler('wee', (lambda bot, update : bot.send_message(chat_id=update.message.chat.id, text="/hoo")) ))
    dispatcher.add_handler(CommandHandler('hoo', (lambda bot, update : bot.send_message(chat_id=update.message.chat.id, text="/wee")) ))
    dispatcher.add_handler(CommandHandler('hi', (lambda bot, update : bot.send_message(chat_id=update.message.chat.id, text="/hi")) ))

    dispatcher.add_handler(CommandHandler('newgame', newgame_handler))

    dispatcher.add_handler(CommandHandler(Secret_Hitler.Game.ACCEPTED_COMMANDS + tuple(COMMAND_ALIASES.keys()), game_command_handler))

    dispatcher.add_handler(CommandHandler('savegame', save_game))
    dispatcher.add_error_handler(handle_error)

    # allows viewing of exceptions
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO) # not sure exactly how this works

    updater.start_polling()
    updater.idle()
