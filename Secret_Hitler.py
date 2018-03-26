import random

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
        print "Message for <{}>: {}".format(self, msg)
        # TODO: Telegram message sending

    def set_role(self, _role):
        self.role = _role
        self.party = _role.replace("Hitler", "Fascist")
        self.send_message("Your secret role is {}".format(self.role))
    def investigate(self, target):
        self.send_message("<{0}> party affiliation is <{0.party}>".format(target))

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

        self.game_state = 0
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
        self.game_state = 1

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
        for p in self.players:
            if p.id == player_str or p.name.find(player_str) != -1:
                return p

        if player_str.isdigit() and int(player_str) < self.num_players:
            return self.players[int(player_str)]
        else:
            return None
    def list_players(self):
        ret = "\n"
        for i in range(len(self.players)):
            ret += "({}) {}\n".format(i, self.players[i])
        return ret
    def add_player(self, _p):
        self.players.append(p)
        self.votes.add(None)

    def select_chancellor(self, target):
        if target in self.termlimited_players or target in self.dead_players:
            return False
        else:
            self.chancellor = target

            Player.global_message("President {} has nominated Chancellor {}.".format(self.president, self.chancellor))
            Player.global_message("Now voting on {}/{}".format(self.president, self.chancellor))
            self.game_state = 2

            return True

    def cast_vote(self, player, vote):
        self.players[self.players.index(player)] = vote
    def election_is_done(self):
        return self.votes.count(None) == self.num_dead_players:
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
            self.anarchy_progress += 1
            if self.anarchy_progress == 3:
                self.anarchy()

            self.advance_presidency(False)

    def president_legislate(self, discard):
        if discard in self.deck[:3]:
            self.deck.remove(discard)
            self.discard.append(discard)
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
                Player.global_message("President ({}) must investigate another player".format(self.president))
                self.president.send_message("Pick a player to investigate\n" + self.list_players())
                self.game_state = 5 # investigation
            elif self.fascist == 3:
                self.game_state = 6 # special election

        if self.fascist == 4 or self.fascist == 5:
            Player.global_message("President ({}) must kill another player".format(self.president))
            self.game_state = 7 # kill
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

    def deck_peek(self, who, num=3):
        who.send_message("".join(self.deck[:num]))
    def special_elect(self, target):
        self.last_nonspecial_president = self.president
        self.president = target
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
        self.game_state = 8

    def game_state_str(self):
        if self.game_state == 0:
            return "Accepting players"
        elif self.game_state == 1:
            return "President nominating a chancellor"
        elif self.game_state == 2:
            return "Election in progress"
        elif self.game_state == 3:
            return "President is legislating"
        elif self.game_state == 4:
            return "Chancellor is legislating"
        elif self.game_state == 4.5:
            return "President/Chancellor are deciding whether to veto"
        elif self.game_state == 5:
            return "President is investigating a player"
        elif self.game_state == 6:
            return "President is nominating a president (special election)"
        elif self.game_state == 7:
            return "President is killing a player"
        elif self.game_state == 8:
            return "Game is over"
    def handle_message(self, from_id, msg):
        if self.game_state == 0:
            for p in players:
                if p.id == from_id:
                    p.name = msg
                    p.send_message("I've set your name to: " + msg)
                    return

            new_player = Player(from_id, from_id)
            self.add_player(new_player)
            new_player.send_message("Welcome to Secret Hitler!  What is your name?")
            return

        from_player = self.str_to_player(from_id)

        if self.game_state == 1 and from_player == self.president:
            new_chancellor = self.str_to_player(msg)
            if new_chancellor == None:
                from_player.send_message("Error: Could not parse player.")
            elif self.select_chancellor(new_chancellor):
                from_player.send_message("You have nominated <{}> for chancellor.".format(new_chancellor))
            else:
                from_player.send_message("Error: <{}> is term-limited/dead.".format(new_chancellor))
        elif self.game_state == 2:
            return
        elif self.game_state == 3:
            return
        elif self.game_state == 4:
            return
        elif self.game_state == 4.5:
            return
        elif self.game_state == 5:
            return
        elif self.game_state == 6:
            return
        elif self.game_state == 7:
            return
        elif self.game_state == 8
            return
    def game_loop(self):
        pass
        # TODO: telegram message receiving

game = Game()

while True:
    game.game_loop()
