import random
from enum import Enum

class Player:
    def __init__(self, _id, _name):
        self.id = _id
        self.name = _name
    def __str__(self):
        return self.name

    @staticmethod
    def global_message(msg):
        print "[ Message for everyone ]\n{}".format(msg)
        # TODO: Telegram channel message
    def send_message(self, msg):
        print "[ Message for {} ]\n{}".format(self, msg)
        # TODO: Telegram message sending

    def set_role(self, _role):
        self.role = _role
        self.party = _role.replace("Hitler", "Fascist")
        self.send_message("Your secret role is {}".format(self.role))
    def investigate(self, target):
        self.send_message("<{0}> party affiliation is <{0.party}>".format(target))
        Player.global_message("{} has investigated {}".format(self, target))

class GameStates(Enum):
    ACCEPT_PLAYERS = 0
    CHANCY_NOMINATION = 1
    ELECTION = 2
    LEG_PRES = 3
    LEG_CHANCY = 4
    VETO_CHOICE = 4.5
    INVESTIGATION = 5
    SPECIAL_ELECTION = 6
    EXECUTION = 7
    GAME_OVER = 8

class Game:
    def __init__(self):
        #self.deck = ['L', 'L', 'L', 'L', 'L', 'L',
        #             'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F']
        #random.shuffle(self.deck)
        self.deck = ['F', 'F', 'L', 'F', 'F', 'L',
                    'F', 'F', 'L', 'F', 'F', 'L', 'F', 'F', 'L', 'F', 'L']
        # TODO: TESTING CODE

        self.discard = []

        self.players = []
        self.president = None
        self.chancellor = None
        self.termlimited_players = set()
        self.dead_players = set()
        # TODO: track CNH

        self.last_nonspecial_president = None
        self.vetoable_polcy = None
        self.president_veto_vote = None
        self.chancellor_veto_vote = None

        self.num_players = 0

        self.votes = []
        self.liberal = 0
        self.fascist = 0
        self.anarchy_progress = 0

        self.game_state = GameStates.ACCEPT_PLAYERS
    def start_game(self):
        # random.shuffle(self.players)
        # NOTE: players will be seated in order they join unless this is uncommented

        self.num_players = len(self.players)
        self.num_alive_players = self.num_players
        self.num_dead_players = 0

        if self.num_players == 5 or self.num_players == 6: # 1F + H
            fascists = random.sample(self.players, 2)
        elif self.num_players == 7 or self.num_players == 8: # 2F + H
            fascists = random.sample(self.players, 3)
        elif self.num_players == 9 or self.num_players == 10: # 3F + H
            fascists = random.sample(self.players, 4)
        else:
            raise Exception("Invalid number of players")

        for p in self.players:
            if p == fascists[0]:
                p.set_role("Hitler")
                if self.num_players <= 6:
                    p.send_message("Fascist: {}".format(fascists[1]))
            elif p in fascists:
                p.set_role("Fascist")
                if self.num_players <= 6:
                    p.send_message("Hitler: {}".format(fascists[0]))
                else:
                    p.send_message("Other Fascist{}: {}\nHitler: {}".format("s" if len(fascists) > 3 else "", ", ".join([ other_p.name for other_p in fascists[1:] if other_p != p ]), fascists[0]))
            else:
                p.set_role("Liberal")

        self.president = self.players[0]
        self.set_game_state(GameStates.CHANCY_NOMINATION)

    @staticmethod
    def str_to_vote(vote_str):
        vote_str = vote_str.lower()
        if vote_str in ("ja", "yes", "y"):
            return True
        elif vote_str in ("nein", "no", "n"):
            return False
        else:
            return None
    @staticmethod
    def str_to_policy(vote_str):
        vote_str = vote_str.lower()
        if vote_str == "f" or vote_str.find("s p i c y") != -1 or vote_str == "fascist":
            return "F"
        elif vote_str == "l" or vote_str.find("") != -1 or vote_str == "lib":
            return "L"
        else:
            return None

    def str_to_player(self, player_str):
        if player_str.isdigit() and int(player_str) > 0 and int(player_str) <= self.num_players:
            return self.players[int(player_str) - 1]
        else:
            for p in self.players:
                if p.name.find(player_str) != -1:
                    return p
            return None
    def id_to_player(self, id):
        for p in self.players:
            if p.id == id:
                return p
        return None
    def list_players(self):
        ret = ""
        for i in range(len(self.players)):
            status = ""
            if self.players[i] == self.president:
                status += " (P)"
            if self.players[i] == self.chancellor:
                status += " (C)"
            if self.players[i] in self.termlimited_players:
                status += " (TL)"
            if self.players[i] in self.dead_players:
                status += " (RIP)"
            ret += "({}) {}{}\n".format(i + 1, self.players[i], status)

        return ret
    def add_player(self, p):
        self.players.append(p)
        self.votes.append(None)
        self.num_players += 1
    def remove_player(self, p):
        if self.game_state == GameStates.ACCEPT_PLAYERS:
            self.players.remove(p)
            self.votes.pop()
            self.num_players -= 1
        elif p in self.dead_players: # TODO probably unnecessary
            index = self.players.index(p)
            self.players.pop(index)
            self.votes.pop(index)
            self.num_players -= 1
            self.num_dead_players -= 1
        else:
            Player.global_message("Player {} left, so this game is self-destructing".format(p))
            self.set_game_state(GameStates.GAME_OVER)

    def select_chancellor(self, target):
        if target in self.termlimited_players or target in self.dead_players or target == self.president:
            return False
        else:
            self.chancellor = target

            Player.global_message("President {} has nominated Chancellor {}.".format(self.president, self.chancellor))
            #Player.global_message("Now voting on {}/{}".format(self.president, self.chancellor))
            self.set_game_state(GameStates.ELECTION)

            return True

    def cast_vote(self, player, vote):
        self.players[self.players.index(player)] = vote
    def list_nonvoters(self):
        return "\n".join([ str(self.players[i]) for i in range(self.num_players) if self.votes[i] is None ])
    def election_is_done(self):
        return self.votes.count(None) == self.num_dead_players
    def election_call(self):
        if self.votes.count(True) > self.num_alive_players / 2:
            return True
        elif self.votes.count(False) > self.num_alive_players / 2:
            return False
        else:
            return None
    def election_results(self):
        return "\n".join([ "{} - {}".format(self.players[i], "ja" if self.votes[i] else "nein") for i in range(self.num_players)])
    def update_termlimits(self):
        self.termlimited_players.clear()
        self.termlimited_players.add(self.chancellor)
        if self.num_players - len(self.dead_players) > 5:
            self.termlimited_players.add(self.president)

    def end_election(self):
        assert self.election_is_done()
        election_result = self.election_call()

        Player.global_message("{}".format("JA!" if election_result else "NEIN!"))
        Player.global_message(self.election_results())

        if election_result:
            if self.fascist >= 3 and self.chancellor.role == "Hitler":
                self.end_game("Fascist", "Hitler was elected chancellor")
            else:
                self.set_game_state(GameStates.LEG_PRES)

            self.update_termlimits()
            self.anarchy_progress = 0
        else:
            self.anarchy_progress += 1
            if self.anarchy_progress == 3:
                self.anarchy()

            self.advance_presidency()

        self.votes = [None] * self.num_players

    def president_legislate(self, discard):
        if discard in self.deck[:3]:
            self.deck.remove(discard)
            self.discard.append(discard)

            self.set_game_state(GameStates.LEG_CHANCY)
            return True
        else:
            return False
    def chancellor_legislate(self, enact):
        if enact in self.deck[:2]:
            self.deck.remove(enact)
            self.discard.append(self.deck.pop(0))

            if self.fascist == 5:
                self.vetoable_polcy = enact
                self.set_game_state(GameStates.VETO_CHOICE)
            else:
                self.pass_policy(enact)
            return True
        else:
            return False
    def check_reshuffle(self):
        if len(self.deck) <= 3: # NOTE: official rules say not to shuffle when there are 3 policies but this is a house rule
            self.deck.extend(self.discard)
            self.discard.clear()

            random.shuffle(self.deck)

            Player.global_message("Deck has been reshuffled.")

    def check_veto(self):
        if False in (self.president_veto_vote, self.chancellor_veto_vote): # no veto
            Player.global_message("{} {} has refused to veto")
            self.pass_policy(self.vetoable_polcy)
            self.vetoable_polcy = None

        elif self.president_veto_vote and self.chancellor_veto_vote: # veto
            Player.global_message("VETO!")

            self.discard.append(self.vetoable_polcy)
            self.check_reshuffle()
            self.vetoable_polcy = None
            self.anarchy_progress

            self.anarchy_progress += 1
            if self.anarchy_progress == 3:
                self.anarchy()

    def pass_policy(self, policy, on_anarchy=False):
        if policy == "L":
            self.pass_liberal()
        else:
            self.pass_fascist(on_anarchy)

        self.check_reshuffle()

        if not on_anarchy and self.game_state == GameStates.LEG_CHANCY: # don't need to wait for other decisison
            self.advance_presidency()
    def pass_liberal(self):
        self.liberal += 1
        Player.global_message("A liberal policy was passed!")

        if self.liberal == 5:
            self.end_game("Liberal", "5 Liberal policies were enacted")
    def pass_fascist(self, on_anarchy):
        self.fascist += 1
        Player.global_message("A fascist policy was passed!")

        if self.fascist == 6:
            self.end_game("Fascist", "6 Fascist policies were enacted")
            return

        if on_anarchy:
            return # any executive powers ignored in anarchy

        if self.num_players in (5,6) and self.fascist == 3:
            self.check_reshuffle()
            Player.global_message("President ({}) is examining top 3 policies".format(self.president))
            self.president.send_message("Top three policies are: ")
            self.deck_peek(self.president, 3)
        else:
            if self.fascist == 2 or (self.fascist == 1 and self.num_players >= 9):
                self.set_game_state(GameStates.INVESTIGATION) # investigation
            elif self.fascist == 3:
                self.set_game_state(GameStates.SPECIAL_ELECTION) # special election

        if self.fascist == 4 or self.fascist == 5:
            self.set_game_state(GameStates.EXECUTION) # kill
    def next_alive_player(self, starting_after):
        target_index = self.players.index(starting_after)
        while self.players[target_index] == starting_after or self.players[target_index] in self.dead_players:
            target_index += 1
            target_index %= self.num_players
        return self.players[target_index]

    def advance_presidency(self):
        if self.last_nonspecial_president == None:
            self.president = self.next_alive_player(self.president)
        else:
            self.president = self.next_alive_player(self.last_nonspecial_president)
            self.last_nonspecial_president = None

        self.chancellor = None
        self.set_game_state(GameStates.CHANCY_NOMINATION)

    def deck_peek(self, who, num=3):
        who.send_message("".join(self.deck[:num]))
    def special_elect(self, target):
        if target == self.president:
            return False # cannot special elect self

        self.last_nonspecial_president = self.president
        self.president = target
        return True

    def kill(self, target):
        if target.role == "Hitler":
            self.end_game("Liberal", "Hitler was killed")
        else:
            self.dead_players.add(target)
            self.num_alive_players -= 1
            self.num_dead_players += 1

    def anarchy(self):
        self.check_reshuffle()
        self.pass_policy(self.deck.pop(0), on_anarchy=True)

        self.termlimited_players.clear()
        self.anarchy_progress = 0

    def end_game(self, winning_party, reason):
        Player.global_message("The {} team wins! ({}.)".format(winning_party, reason))
        self.game_state = GameStates.GAME_OVER

    def set_game_state(self, new_state):
        self.game_state = new_state

        if self.game_state == GameStates.CHANCY_NOMINATION:
            Player.global_message("President {} must nominate a chancellor".format(self.president))
            self.president.send_message("Pick your chancellor:\n" + self.list_players())
        elif self.game_state == GameStates.ELECTION:
            Player.global_message("Election: Vote on President {} and Chancellor {}".format(self.president, self.chancellor))
            for p in self.players: # send individual messages to clarify who you're voting on
                if p not in self.dead_players:
                    p.send_message("{}/{} vote:".format(self.president, self.chancellor))
        elif self.game_state == GameStates.LEG_PRES:
            Player.global_message("Legislative session in progress (waiting on President {})".format(self.president))
            self.president.send_message("Pick a policy to discard:")
            self.deck_peek(self.president, 3)
        elif self.game_state == GameStates.LEG_CHANCY:
            Player.global_message("Legislative session in progress (waiting on Chancellor {})".format(self.chancellor))
            self.chancellor.send_message("Pick a policy to enact:")
            self.deck_peek(self.chancellor, 2)
        elif self.game_state == GameStates.VETO_CHOICE:
            Player.global_message("President ({}) and Chancellor ({}) are deciding whether to veto (both must agree to do so)".format(self.president, self.chancellor))
            self.president.send_message("Would you like to veto?")
            self.chancellor.send_message("Would you like to veto?")
            self.president_veto_vote = None
            self.chancellor_veto_vote = None
        elif self.game_state == GameStates.INVESTIGATION:
            Player.global_message("President ({}) must investigate another player".format(self.president))
            self.president.send_message("Pick a player to investigate:\n" + self.list_players())
        elif self.game_state == GameStates.SPECIAL_ELECTION:
            Player.global_message("Special Election: President ({}) must choose the next presidential candidate".format(self.president))
            self.president.send_message("Pick the next presidential candidate:\n" + self.list_players())
        elif self.game_state == GameStates.EXECUTION:
            Player.global_message("President ({}) must kill someone".format(self.president))
            self.president.send_message("Pick someone to kill:\n" + self.list_players())
        elif self.game_state == GameStates.GAME_OVER:
            Player.global_message("\n".join(["{} - {}".format(p, p.role) for p in self.players]))
            # reveal all player roles when the game has ended

    def handle_message(self, from_id, msg):
        print "[{}] {}".format(from_id, msg)
        from_player = self.id_to_player(from_id)

        if from_player is not None:
            if msg.find("/listplayers") != -1:
                from_player.send_message(self.list_players())
                return
            if self.game_state != GameStates.ACCEPT_PLAYERS:
                if msg.find("/boardstats") != -1:
                    from_player.send_message("{} Fascist / {} Liberal".format(self.fascist, self.liberal))
                    return
                elif msg.find("/deckstats") != -1:
                    from_player.send_message("{} tiles in deck, {} in discard. {} F / {} L in deck/discard (combined)".format(len(self.deck), len(self.discard), 11 - self.fascist, 6 - self.liberal))
                    return
                elif msg.find("/anarchystats") != -1:
                    from_player.send_message("Election tracker is at {}/3".format(self.anarchy_progress))
                    return
        if self.game_state == GameStates.ACCEPT_PLAYERS:
            if from_player is None and self.num_players < 10:
                new_player = Player(from_id, from_id)
                self.add_player(new_player)
                new_player.send_message("Welcome to Secret Hitler!  What is your name?")
            elif msg.find("/startgame") != -1:
                if self.num_players >= 5:
                    self.start_game()
                else:
                    from_player.send_message("Error: only {} players".format(self.num_players))
            elif msg.find("/leave") != -1:
                self.remove_player(from_player)
                from_player.send_message("Successfully left game!")
            else:
                from_player.name = msg # TODO: ensure name validity/no duplicates
                from_player.send_message("I've set your name to: " + msg)
        elif self.game_state == GameStates.CHANCY_NOMINATION and from_player == self.president:
            new_chancellor = self.str_to_player(msg)
            if new_chancellor == None:
                from_player.send_message("Error: Could not parse player.")
            elif self.select_chancellor(new_chancellor):
                from_player.send_message("You have nominated {} for chancellor.".format(new_chancellor))
            else:
                from_player.send_message("Error: {} is term-limited/dead/yourself.".format(new_chancellor))
        elif self.game_state == GameStates.ELECTION and msg.find("/blame") != -1:
            from_player.send_message("People who haven't yet voted:\n" + self.list_nonvoters())
        elif self.game_state == GameStates.ELECTION and from_player in self.players and from_player not in self.dead_players:
            vote = Game.str_to_vote(msg)
            if vote is None:
                from_player.send_message("Vote not recognized")
            elif vote:
                self.votes[self.players.index(from_player)] = True
                from_player.send_message("Ja vote recorded")
            else:
                self.votes[self.players.index(from_player)] = False
                from_player.send_message("Nein vote recorded")

            if self.election_is_done():
                self.end_election()
            # TODO: expedite the game by giving pres/chancy their policies before the election is finished
        elif self.game_state == GameStates.LEG_PRES and from_player == self.president:
            policy = Game.str_to_policy(msg)
            if policy is None:
                from_player.send_message("Error: Policy could not be parsed")
            elif self.president_legislate(policy):
                from_player.send_message("Thanks!")
            else:
                from_player.send_message("Error: Given policy not in top 3")
        elif self.game_state == GameStates.LEG_CHANCY and from_player == self.chancellor:
            policy = Game.str_to_policy(msg)
            if policy is None:
                from_player.send_message("Error: Policy could not be parsed")
            elif self.chancellor_legislate(policy):
                from_player.send_message("Thanks!")
            else:
                from_player.send_message("Error: Given policy not in top 2")
        elif self.game_state == GameStates.VETO_CHOICE and from_player == self.president:
            vote = self.str_to_vote(msg)
            if vote is None:
                from_player.send_message("Error: Vote could not be parsed")
            else:
                self.president_veto_vote = vote
            self.check_veto()
        elif self.game_state == GameStates.VETO_CHOICE and from_player == self.chancellor:
            vote = self.str_to_vote(msg)
            if vote is None:
                from_player.send_message("Error: Vote could not be parsed")
            else:
                self.chancellor_veto_vote = vote
            self.check_veto()
        elif self.game_state == GameStates.INVESTIGATION and from_player == self.president:
            target = self.str_to_player(msg)
            if target == None:
                from_player.send_message("Error: Could not parse player.")
            else:
                from_player.investigate(target)
                self.advance_presidency()
        elif self.game_state == GameStates.SPECIAL_ELECTION and from_player == self.president:
            new_president = self.str_to_player(msg)
            if new_president == None:
                from_player.send_message("Error: Could not parse player.")
            elif self.special_elect(new_president):
                from_player.send_message("You have nominated {} for president.".format(new_president))
                self.set_game_state(GameStates.CHANCY_NOMINATION)
            else:
                from_player.send_message("Error: you can't nominate yourself for president.".format(new_president))
        elif self.game_state == GameStates.EXECUTION and from_player == self.president:
            if msg.lower().find("me too thanks") != -1:
                from_player.send_message("You have killed yourself.")
                self.kill(from_player)
                self.advance_presidency()
                return

            target = self.str_to_player(msg)
            if target == None:
                from_player.send_message("Error: Could not parse player.")
            elif from_player == target:
                from_player.send_message("You are about to kill yourself.  This is technically allowed by the rules, but why are you like this?")
                from_player.send_message("Reply 'me too thanks' to confirm suicide")
            else:
                self.kill(target)
                self.advance_presidency()
                from_player.send_message("You have killed {}.".format(target))
    def game_loop(self):
        id = raw_input("\tEnter Origin ID: ")
        message = raw_input("\tEnter Message: ")
        print "[{}] {}".format(id, message)
        self.handle_message(id, message)

game = Game()
game.add_player(Player("1", "A"))
game.add_player(Player("2", "B"))
game.add_player(Player("3", "C"))
game.add_player(Player("4", "D"))
game.add_player(Player("5", "E"))
game.add_player(Player("6", "F"))
game.add_player(Player("7", "G"))
game.handle_message("3", "/startgame")

game.handle_message("1", "D") # 1

game.handle_message("1", "ja")
game.handle_message("2", "ja")
game.handle_message("3", "ja")
game.handle_message("4", "nein")
game.handle_message("5", "ja")
game.handle_message("6", "nein")
game.handle_message("7", "ja")

game.handle_message("1", "L")
#game.handle_message("1", "F")
game.handle_message("4", "F")
#game.handle_message("4", "L")

game.handle_message("2", "E") # 2

game.handle_message("1", "ja")
game.handle_message("2", "ja")
game.handle_message("3", "ja")
game.handle_message("4", "nein")
game.handle_message("5", "ja")
game.handle_message("6", "nein")
game.handle_message("7", "ja")

game.handle_message("2", "L")
#game.handle_message("2", "F")
game.handle_message("5", "F")
#game.handle_message("5", "L")

game.handle_message("2", "E") # inv

game.handle_message("3", "F") # 3

game.handle_message("1", "ja")
game.handle_message("2", "ja")
game.handle_message("3", "ja")
game.handle_message("4", "nein")
game.handle_message("5", "ja")
game.handle_message("6", "nein")
game.handle_message("7", "ja")

game.handle_message("3", "L")
#game.handle_message("3", "F")
game.handle_message("6", "F")
#game.handle_message("6", "L")

game.handle_message("3", "B") # se

game.handle_message("2", "G") # 4

game.handle_message("1", "ja")
game.handle_message("2", "ja")
game.handle_message("3", "ja")
game.handle_message("4", "nein")
game.handle_message("5", "ja")
game.handle_message("6", "nein")
game.handle_message("7", "ja")

game.handle_message("2", "L")
#game.handle_message("4", "F")
game.handle_message("7", "F")
#game.handle_message("7", "L")

game.handle_message("2", "me too thanks") # execution

game.handle_message("1", "/boardstats")
print game.deck
# print list(game.dead_players)[0]

# while True:
#     game.game_loop()
