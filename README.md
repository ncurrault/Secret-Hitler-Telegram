Secret-Hitler-Telegram
===

A Telegram bot that allows users to play Secret Hitler.

## Special Commands

* Available at any time
  * /listplayers - list all players (with annotations as described below)
  * /boardstats - list the number of each type of policy passed
  * /deckstats - get number of tiles in deck, discard, and public knowledge about policy-type distribution
  * /anarchystats - get status of election tracker (number of failed elections/anarchies)
* In ACCEPT_PLAYERS game state
  * /creategame - start a game with global messages in the current chat
  * /joingame - join the game occurring in this chat
  * /leave - leave a game (only valid once it has not started)
  * /changename - change your nickname
  * /startgame - deal out roles and begin the game!
* At appropriate points in the game
  * /blame - list all players who haven't voted in an election
  * /ja - Ja!
  * /nein - Nein
  * /nominate [PLAYERNAME] - nominate someone for chancellor or presidential candidate (in the case of special election)
  * /kill [PLAYERNAME] - kill another player
  * /investigate [PLAYERNAME] - investigate the party affiliation of another player
  * /enact [POLICY] - as chancellor, pick a policy to enact
  * /discard [POLICY] - as president or chancellor, pick a policy to discard

## Player status abbreviations
* (P) indicates a current president/presidential candidate
* (C) indicates a current president/presidential candidate
* (TL) indicates a term-limited player (ineligible for any chancellor nominations)
* (RIP) indicates a dead player

## API Key

The api key is stored in API_key.txt but withheld with .gitignore. To replicate this project, make a Telegram bot by messaging \@BotFather and pasting the resulting API key there.

## License/Attribution

Secret Hitler is designed by Max Temkin, Mike Boxleiter, Tommy Maranges and
illustrated by Mackenzie Schubert.

This game is licensed as per the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/) license.
