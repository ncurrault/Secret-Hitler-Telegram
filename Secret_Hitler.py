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
    def send_message(self, msg):
        print "Message for <{}>: {}".format(self, msg)
        # TODO: actual message with Telegram
    def get_input(self, msg, options):
        self.send_message(msg)
        return raw_input("Input from player <{}>: ".format(self))
        # TODO: some threading thing with Telegram integration?

    def set_role(self, _role):
        self.role = _role
        self.party = _role.replace("Hitler", "Fascist")
        self.send_message("Your secret role is {}".format(self.role))

class Game:
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

    def __init__(self):
        self.deck = ['L', 'L', 'L', 'L', 'L', 'L',
                     'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F']
        random.shuffle(self.deck)
        self.discard = []

        self.players = []
        self.significant_players = { "President": None, "Chancellor": None, "Term-Limited": set(), "Dead": set() }
        self.votes = []
        self.liberal = 0
        self.fascist = 0
        self.anarchy_progress = 0

        self.game_state = 0

    def start_game(self):
        random.shuffle(self.players)

        self.num_players = len(self.players)

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

        self.significant_players["President"] = players[0]
        self.game_state = 1

    def str_to_player(self, player_str):
        if player_str.isdigit() and int(player_str) < self.num_players:
            return self.players[int(player_str)]
        else:
            for p in self.players:
                if str(p).find(player_str) != -1:
                    return p
            return None
    @staticmethod
    def str_to_vote(vote_str):
        vote_str = vote_str.lower()
        if vote_str in ("ja", "yes", "y"):
            return True
        elif vote_str in ("nein", "no", "n"):
            return False
        else:
            return None

    def select_chancellor(self, target):
        if target in self.significant_players["Term-Limited"] or target in self.significant_players["Dead"]:
            return False
        else:
            self.significant_players["Chancellor"] = target
            return True
    def count_votes(self):
        if self.votes.count(None) == 0:
            return self.votes.count(True) > self.num_players / 2
        else:
            return None
    def end_election(self, president, chancellor):
        assert count_votes()
        if self.fascist >= 3 and chancellor.role == "Hitler":
            self.end_game("Fascist", "Hitler was elected chancellor!")

    def president_legislate(self, discard):
        assert discard in self.deck[:3]
        self.deck.remove(discard)
        self.discard.append(discard)
    def chancellor_legislate(self, enact):
        assert enact in self.deck[:2]
        self.deck.remove(enact)
        self.discard.append(self.deck.pop(0))

        self.check_reshuffle()

        if enact == "L":
            self.pass_liberal()
        else:
            self.pass_fascist()

    def pass_fascist(self, on_anarchy=False):
        self.fascist += 1
        Player.global_message("A fascist policy was passed!")

        if self.fascist == 6:
            self.end_game("Fascist", "6 Fascist policies were enacted")

        if not on_anarchy:
            if self.num_players in (5,6) and self.fascist == 3:
                Player.global_message("President is examining top 3 policies")
                self.significant_players["President"].send_message("Top three policies are: " self.deck_peek())
            else:
                if self.fascist == 2 or (self.fascist == 1 and self.num_players >= 9):
                    Player.global_message("President must investigate another player")
                    self.significant_players["President"].send_message("Pick a player to investigate\n" + self.list_players())
                    self.game_state = 5 # investigation
                elif self.fascist == 3:
                    self.game_state = 6 # special election

            if self.fascist == 4 or self.fascist == 5:
                self.game_state = 7 # kill

    def pass_liberal(self):
        self.liberal += 1
        Player.global_message("A liberal policy was passed!")

        if self.liberal == 5:
            self.end_game("Liberal", "5 Liberal policies were enacted")

    def deck_peek(self, who, num=3):
        who.send_message("".join(self.deck[:num]))
    def investigate(self, investigator, target):
        investigator.send_message("<{0}> party affiliation is <{0.party}>".format(target))
    def kill(self, target):
        if target.role == "Hitler":
            self.end_game("Liberal", "Hitler was killed!")
        else:
            self.significant_players["Dead"].add(target)
    def end_game(self, winning_party, reason):
        Player.global_message("The {} team wins!\n{}".format(winning_party, reason))
        self.game_state = 8

    def game_loop(self):
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


game = Game()
while True:
    game.game_loop()
