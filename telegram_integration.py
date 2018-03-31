# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import Secret_Hitler
import telegram
from telegram.ext import Updater, CommandHandler, Filters
import logging

with open("API_key.txt", "r") as f:
    API_KEY = f.read().rstrip()

bot = telegram.Bot(token=API_KEY)
updater = Updater(token=API_KEY)
dispatcher = updater.dispatcher

game = None

def start_handler(bot, update):
    # TODO: specify that the DM conversation will contain private info
    bot.send_message(chat_id=update.message.chat_id, text="Hi! This bot runs games of Secret Hitler via Telegram. Add me to a chat with all players and send the /newgame command there. This will specify where all public information is posted.")
def help_handler(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="""Command List:
/changename [NEW NAME] - change your nickname (default is your Telegram first name)
/nominate [PLAYER NAME] - nominate someone for chancellor or presidential candidate (in the case of special election)
/kill [PLAYER NAME] - kill another player
/investigate [PLAYER NAME] - investigate the party affiliation of another player
/enact [POLICY] - as chancellor, pick a policy to enact
/discard [POLICY] - as president or chancellor, pick a policy to discard

/listplayers - list all players with annotations for Pres, Chancy, term-limits, and deaths
/boardstats - list the number of each type of policy passed
/deckstats - get number of tiles in deck, discard, and public info about type distribution
/anarchystats - get status of election tracker
/newgame - start a game with global messages in the current chat
/joingame - join the game occurring in a chat
/leave - leave a game (only valid if it has not started)
/startgame - deal out roles and begin the game!
/ja - Ja!
/nein - Nein
/blame - list all players who haven't voted in an election""")
def newgame_handler(bot, update):
    global game
    chat_id = update.message.chat.id
    if game is not None and game.game_state != Secret_Hitler.GameStates.GAME_OVER and update.message.text.find("confirm") == -1:
        bot.send_message(chat_id=chat_id, text="Warning: game already in progress here. Reply '/newgame confirm' to confirm")
    else:
        game = Secret_Hitler.Game(chat_id)
        bot.send_message(chat_id=chat_id, text="Created game! /joingame to join, /startgame to start")

def parse_message(msg):
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
    command, args = parse_message(update.message.text)
    if command in COMMAND_ALIASES.keys():
        command = COMMAND_ALIASES[command]
    player_id, chat_id = update.message.from_user.id, update.message.chat.id

    global game
    if game is None:
        bot.send_message(chat_id=chat_id, text="Error: no game in progress here")
    else:
        player = game.get_player_by_id(player_id) or Secret_Hitler.Player(player_id, update.message.from_user.first_name)
        # use player object from game if it exists

        try:
            reply = game.handle_message(player, command, args)

            if reply: # reply is None if no response is necessary
                if command in Secret_Hitler.Game.MARKDOWN_COMMANDS: # these require links/tagging
                    bot.send_message(chat_id=chat_id, text=reply, parse_mode=telegram.ParseMode.MARKDOWN)
                else:
                    bot.send_message(chat_id=chat_id, text=reply)
        except Secret_Hitler.GameOverException:
            return

# Credit (TODO: actual attribution): https://github.com/CaKEandLies/Telegram_Cthulhu/blob/master/cthulhu_game_bot.py#L63
def feedback_handler(bot, update, args=None):
    if args and len(args) > 0:
        feedback = open("feedback.txt", "a")
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

if __name__ == "__main__":
    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(CommandHandler('help', help_handler))
    dispatcher.add_handler(CommandHandler('feedback', feedback_handler, pass_args=True))

    # memes
    dispatcher.add_handler(CommandHandler('wee', (lambda bot, update : bot.send_message(chat_id=update.message.chat.id, text="/hoo")) ))
    dispatcher.add_handler(CommandHandler('hoo', (lambda bot, update : bot.send_message(chat_id=update.message.chat.id, text="/wee")) ))
    dispatcher.add_handler(CommandHandler('hi', (lambda bot, update : bot.send_message(chat_id=update.message.chat.id, text="/hi")) ))

    dispatcher.add_handler(CommandHandler('newgame', newgame_handler))

    dispatcher.add_handler(CommandHandler(Secret_Hitler.Game.ACCEPTED_COMMANDS + tuple(COMMAND_ALIASES.keys()), game_command_handler))

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO) # not sure exactly how this works

    updater.start_polling()
    updater.idle()
