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
        print "Message for everyone: {}".format(msg)
        # TODO: Telegram channel message
    def send_message(self, msg):
        print "Message for {}: {}".format(self, msg)
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
        self.deck = ['L', 'L', 'L', 'L', 'L', 'L',
                     'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F']
        random.shuffle(self.deck)
        self.discard = []

        self.players = []
        self.president = None
        self.chancellor = None
        self.termlimited_players = set()
        self.dead_players = set()
        self.last_nonspecial_president = None

        self.votes = []
        self.liberal = 0
        self.fascist = 0
        self.anarchy_progress = 0

        self.game_state = GameStates.ACCEPT_PLAYERS
    def start_game(self):
        random.shuffle(self.players)

        self.num_players = len(self.players)
        self.num_alive_players = self.num_players
        self.num_dead_players = 0

        if self.num_players == 5 or self.num_players == 6: # 1F + H
            fascists = random.sample(players, 2)
        elif self.num_players == 7 or self.num_players == 8: # 2F + H
            fascists = random.sample(players, 3)
        elif self.num_players == 9 or self.num_players == 10: # 3F + H
            fascists = random.sample(players, 4)
        else:
            raise Exception("Invalid number of players")

        for p in players:
            if p == fascists[0]:
                p.set_role("Hitler")
                if self.num_players <= 6:
                    p.send_message("Fascist: {}".format(fascists[1]))
            elif p in fascists:
                p.set_role("Fascist")
                if self.num_players <= 6:
                    p.send_message("Hitler: {}".format(fascists[0]))
                else:
                    p.send_message("Other Fascists: {}\nHitler: {}".format(", ".join(fascists[1:]), fascists[0]))
            else:
                p.set_role("Liberal")

        self.president = players[0]
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
        ret = "\n"
        for i in range(len(self.players)):
            ret += "({}) {}\n".format(i + 1, self.players[i])

        # TODO: add notes next to players indicating TL, RIP, CNH, etc.
        return ret
    def add_player(self, _p):
        self.players.append(p)
        self.votes.add(None)

    def select_chancellor(self, target):
        if target in self.termlimited_players or target in self.dead_players or target == self.president:
            return False
        else:
            self.chancellor = target

            Player.global_message("President {} has nominated Chancellor {}.".format(self.president, self.chancellor))
            Player.global_message("Now voting on {}/{}".format(self.president, self.chancellor))
            self.set_game_state(GameStates.ELECTION)

            return True

    def cast_vote(self, player, vote):
        self.players[self.players.index(player)] = vote
    def election_is_done(self):
        return self.votes.count(None) == self.num_dead_players
    def election_call(self):
        if self.votes.count(True) > self.num_alive_players / 2:
            return True
        elif self.votes.count(False) > self.num_alive_players / 2:
            return False
        else:
            return None
    def end_election(self):
        assert self.election_is_done()
        # TODO: expedite the game by giving pres/chancy their policies before the election is finished

        if self.election_call():
            if self.fascist >= 3 and chancellor.role == "Hitler":
                self.end_game("Fascist", "Hitler was elected chancellor!")
            else:
                self.set_game_state(GameStates.LEG_PRES)
        else:
            self.anarchy_progress += 1
            if self.anarchy_progress == 3:
                self.anarchy()

            self.advance_presidency(False)

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

            if enact == "L":
                self.pass_liberal()
            else:
                self.pass_fascist()

            self.check_reshuffle()

            # TODO: implement veto power

            self.advance_presidency(True)

            return True
        else:
            return False
    def check_reshuffle(self):
        if len(self.deck) <= 3: # NOTE: official rules say not to shuffle when there are 3 policies but this is a house rule
            self.deck.extend(self.discard)
            self.discard.clear()

            random.shuffle(self.deck)

            Player.global_message("Deck has been reshuffled.")

    def pass_liberal(self):
        self.liberal += 1
        Player.global_message("A liberal policy was passed!")

        if self.liberal == 5:
            self.end_game("Liberal", "5 Liberal policies were enacted")
    def pass_fascist(self, on_anarchy=False):
        self.fascist += 1
        Player.global_message("A fascist policy was passed!")

        if self.fascist == 6:
            self.end_game("Fascist", "6 Fascist policies were enacted")

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
            self.set_game_state(GameStates.INVESTIGATION) # kill
    def next_alive_player(self, player):
        target_index = self.players.index(target)
        while self.players[target_index] == player or self.players[target_index] in self.dead_players:
            target_index += 1
            target_index %= self.num_players
        return self.players[target_index]

    def advance_presidency(self, update_term_limits=True):
        if update_term_limits:
            self.termlimited_players.clear()
            self.termlimited_players.add(self.chancellor)
            if self.num_players - len(self.dead_players) > 5:
                self.termlimited_players.add(self.president)

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
            self.end_game("Liberal", "Hitler was killed!")
        else:
            self.dead_players.add(target)
            self.num_alive_players -= 1
            self.num_dead_players += 1

    def anarchy(self):
        self.check_reshuffle()
        if self.deck.pop(0) == "L":
            self.pass_liberal()
        else:
            self.pass_fascist(on_anarchy=True)

        self.termlimited_players.clear()
        self.anarchy_progress = 0

    def end_game(self, winning_party, reason):
        Player.global_message("The {} team wins!\n{}".format(winning_party, reason))
        self.game_state = GameStates.GAME_OVER

    def set_game_state(self, new_state):
        self.game_state = new_state

        if self.game_state == GameStates.CHANCY_NOMINATION:
            Player.global_message("President {} must nominate a chancellor".format(self.president))
            self.president.send_message("Pick your chancellor:\n" + self.list_players())
        elif self.game_state == GameStates.ELECTION:
            Player.global_message("Election: Vote on President {} and Chancellor {}".format(self.president, self.chancellor))
            # TODO: send individual messages to clarify who you're voting on
        elif self.game_state == GameStates.LEG_PRES:
            Player.global_message("Legislative session in progress (waiting on President {})".format(self.president))
            self.president.send_message("Pick a policy to discard:")
            self.deck_peek(self.president, 3)
        elif self.game_state == GameStates.LEG_CHANCY:
            Player.global_message("Legislative session in progress (waiting on Chancellor {})".format(self.chancellor))
            self.president.send_message("Pick a policy to enact:")
            self.deck_peek(self.chancellor, 2)
        elif self.game_state == GameStates.VETO_CHOICE:
            Player.global_message("President ({}) and Chancellor ({}) are deciding whether to veto (both must agree to do so)".format(self.president, self.chancellor))
            self.president.send_message("Would you like to veto?")
            self.chancellor.send_message("Would you like to veto?")
        elif self.game_state == GameStates.INVESTIGATION:
            Player.global_message("President ({}) must investigate another player".format(self.president))
            self.president.send_message("Pick a player to investigate:\n" + self.list_players())
        elif self.game_state == GameStates.SPECIAL_ELECTION:
            Player.global_message("Special Election: President ({}) must choose the next presidential candidate".format(self.president))
            self.president.send_message("Pick the next presidential candidate:\n" + self.list_players())
        elif self.game_state == GameStates.INVESTIGATION:
            Player.global_message("President ({}) must kill someone".format(self.president))
            self.president.send_message("Pick someone to kill:\n" + self.list_players())

    def handle_message(self, from_id, msg):
        if self.game_state == GameStates.ACCEPT_PLAYERS:
            for p in players:
                if p.id == from_id:
                    p.name = msg
                    p.send_message("I've set your name to: " + msg)
                    return

            new_player = Player(from_id, from_id)
            self.add_player(new_player)
            new_player.send_message("Welcome to Secret Hitler!  What is your name?")
            return

        from_player = self.id_to_player(from_id)

        # TODO: anytime commands

        if self.game_state == GameStates.CHANCY_NOMINATION and from_player == self.president:
            new_chancellor = self.str_to_player(msg)
            if new_chancellor == None:
                from_player.send_message("Error: Could not parse player.")
            elif self.select_chancellor(new_chancellor):
                from_player.send_message("You have nominated {} for chancellor.".format(new_chancellor))
            else:
                from_player.send_message("Error: {} is term-limited/dead/yourself.".format(new_chancellor))
        elif self.game_state == GameStates.ELECTION and from_player in self.players and from_player not in self.dead_players:
            vote = Game.str_to_vote(msg)
            if vote is None:
                from_player.send_message("Vote not recognized")
            elif vote:
                self.votes[self.players.index[from_player]] = True
                from_player.send_message("Ja vote recorded")
            else:
                self.votes[self.players.index[from_player]] = False
                from_player.send_message("Nein vote recorded")

            if self.election_is_done():
                self.end_election()
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
        elif self.game_state == GameStates.VETO_CHOICE:
            return # TODO: implement veto power
        elif self.game_state == GameStates.INVESTIGATION and from_player == self.president:
            target = self.str_to_player(msg)
            if target == None:
                from_player.send_message("Error: Could not parse player.")
            else:
                from_player.investigate(target)
        elif self.game_state == GameStates.SPECIAL_ELECTION and from_player == self.president:
            new_president = self.str_to_player(msg)
            if new_president == None:
                from_player.send_message("Error: Could not parse player.")
            elif self.select_chancellor(new_president):
                from_player.send_message("You have nominated {} for president.".format(new_president))
            else:
                from_player.send_message("Error: you can't nominate yourself for president.".format(new_president))
        elif self.game_state == GameStates.INVESTIGATION and from_player == self.president:
            if msg.lower().find("me too thanks") != -1:
                from_player.send_message("You have killed yourself.")
                self.kill(from_player)
                return

            target = self.str_to_player(msg)
            if target == None:
                from_player.send_message("Error: Could not parse player.")
            elif from_player == target:
                from_player.send_message("You are about to kill yourself.  This is technically allowed by the rules, but why are you like this?")
                from_player.send_message("Reply 'me too thanks' to confirm suicide")
            else:
                self.kill(target)
                from_player.send_message("You have killed {}.".format(target))
    def game_loop(self):
        pass
        # TODO: telegram message receiving

game = Game()

while True:
    game.game_loop()
