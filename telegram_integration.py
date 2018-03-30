import Secret_Hitler
import telegram
from telegram.ext import Updater, CommandHandler, Filters
import re

with open("API_key.txt", "r") as f:
    API_KEY = f.read().rstrip()

bot = telegram.Bot(token=API_KEY)
updater = Updater(token=API_KEY)
dispatcher = updater.dispatcher

# TODO: if this fails try one-game setup
chat_games = {}
player_games = {}

def start_handler(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hi! This bot runs games of Secret Hitler via Telegram. Add me to a chat with all players and send the /newgame command there. This will specify where all public information is posted.")
def help_handler(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="""Command List:
/listplayers - list all players with annotations for Pres, Chancy, term-limits, and deaths
/boardstats - list the number of each type of policy passed
/deckstats - get number of tiles in deck, discard, and public info about type distribution
/anarchystats - get status of election tracker
/creategame - start a game with global messages in the current chat
/joingame - join the game occurring in a chat
/leave - leave a game (only valid if it has not started)
/changename [NEW NAME] - change your nickname (default is your Telegram first name)
/startgame - deal out roles and begin the game!
/ja - Ja!
/nein - Nein
/blame - list all players who haven't voted in an election
/nominate [PLAYER NAME] - nominate someone for chancellor or presidential candidate (in the case of special election)
/kill [PLAYER NAME] - kill another player
/investigate [PLAYER NAME] - investigate the party affiliation of another player
/enact [POLICY] - as chancellor, pick a policy to enact
/discard [POLICY] - as president or chancellor, pick a policy to discard""")
def newgame_handler(bot, update):
    # TODO: issue with this command
    chat_id = update.message.chat.id
    if chat_id in chat_games.keys() \
        and chat_games[chat_id].game_state != Secret_Hitler.GameStates.GAME_OVER \
        and update.message.text.lower().find("confirm") == -1:
        bot.send_message(chat_id=chat_id, text="Warning: game already in progress here. Reply '/newgame confirm' to confirm")
    else:
        if chat_games.get(chat_id):
            chat_games[chat_id].set_game_state(GameStates.GAME_OVER) # reveals player roles
            for p in chat_games[chat_id].players:
                player_games[p] = None #del player_games[p]
        print 1
        chat_games[chat_id] = Secret_Hitler.Game(chat_id)
        print 2
        bot.send_message(chat_id=chat_id, text="Created game! /joingame to join, /startgame to start")
        print 3

def parse_message(msg):
    command = msg.split()[0]
    if command.endswith(bot.username):
        command = command[1:command.find("@")]
    args = msg.split()[1:]
    if len(args) == 0:
        args = "" #None
    else:
        args = " ".join(args)
    return command, args
def game_command_handler(bot, update):
    command, args = parse_message(update.message.text)
    player_id, chat_id = update.message.from_user.id, update.message.chat.id

    source_game = player_games.get(player_id) or chat_games.get(chat_id)
    if source_game is None:
        bot.send_message(chat_id=chat_id, text="Error: no game in progress here")
    else:
        player = Secret_Hitler.Player(player_id, update.message.from_user.first_name)
        # create new player, only to be used if player is not in game currently

        for candidate in source_game.players:
            if candidate.id == player_id:
                player = candidate
                break
        try:
            reply = source_game.handle_message(player, command, args)
            if reply:
                bot.send_message(chat_id=chat_id, text=reply)
        except Secret_Hitler.GameOverException:
            for p in source_game.players:
                player_games[p] = None #del player_games[p]

if __name__ == "__main__":
    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(CommandHandler('help', help_handler))
    dispatcher.add_handler(CommandHandler('newgame', newgame_handler))

    dispatcher.add_handler(CommandHandler(Secret_Hitler.Game.ACCEPTED_COMMANDS, game_command_handler))

    updater.start_polling()
    updater.idle()
