from inspect import getsource
from hashlib import sha256

class Flag:
    def __init__(self, shorthand = " ", data = None):
        self.shorthand=shorthand
        self.data = data

    def __str__(self):
        return self.shorthand

    __repr__ = __str__

    @property
    def uuid(self):
        return sha256(getsource(self.__class__).encode()).hexdigest()
    def __eq__(self, other):  # should be overwritten for more interesting flags.
        if not isinstance(other, Flag):
            if isinstance(other, Card):
                return other.__eq__(self)
            return NotImplemented
        return self.flag_eq(other)

    def __sub__(self, other):
        return NotImplemented

    def flag_eq(self, other): # other is guaranteed to be a flag
        if self.data and other.data:
            return other.shorthand == self.shorthand and other.data == self.data
        else:
            return other.shorthand == self.shorthand

class Value(Flag):
    def __init__(self, data = None):
        super().__init__("V", data)

    def __str__(self):
        if self.data:
            return self.data # self.data should be a string "R3", "B4" etc
        return self.shorthand

    __repr__ = __str__

class Touched(Flag):
    def __init__(self, data = None):
        super().__init__("T", data)

class Card:
    def __init__(self, flags = None):
        if not flags: flags = []
        if isinstance(flags, (list, tuple)):
            self.flags = list(flags)
        else:
            self.flags = [flags]

    def __str__(self):
        return str(Value() - self)

    def __repr__(self):
        return repr(self.flags)

    def __eq__(self, other):
        if isinstance(other, Flag):
            return other in self.flags
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, Flag):
            if other not in self.flags:
                self.flags.append(other)
            return self
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Flag):
            if other in self.flags:
                self.flags.remove(other)
            return self
        return NotImplemented

    def __rsub__(self, other):  # very sus, but subtraction was never commutative anyway
        if isinstance(other, Flag):
            if other in self.flags:
                return self.flags[self.flags.index(other)]
            return None
        return NotImplemented

class Cards: #
    def __getitem__(self, index): # here index is the hand offset, so 0 means the current player and non zero numbers are other players
        return self.cards[index]

    def __str__(self):
        line = lambda L: f"[{', '.join(str(x) for x in L)}]"
        return  line(line(L) for L in self.cards)

    def __repr__(self):
        return repr(self.cards)

    def move_cards(self):
        self.cards = self.cards[1:] + [self.cards[0]]

class Stack:
    def __init__(self, Suit, Rank = 0):
        self.suit = Suit
        self.rank = Rank

    def __str__(self):
        return self.suit + str(self.rank)

    __repr__ = __str__

    def fits(self, card):
        return (Value() - card).data == self.suit + str(self.rank + 1)

    def play(self):
        self.rank += 1

class Game:
    version = "No version given"
    debug = False
    def __init__(self, number_of_players):
        from random import shuffle
        self.suits = ("R", "B", "Y", "G", "W")
        self.ranks = ("1", "1", "1", "2", "2", "3", "3", "4", "4", "5")
        self.deck = [Value(S+R) for S in self.suits for R in self.ranks]
        # note how each card is represented by a single `Value` flag here, rather than by a Card object here
        # Card objects hold potentially multiple flags, but these cards currently can't. In theory you could have a
        # convention where you assign flags to cards in the draw pile, but given that you know very little about them
        # it seems unecessary.
        shuffle(self.deck)
        self.cards_left_in_deck = True # only used at the end of the game
        self.turns_remaining = number_of_players # only used at the end of the game, together with cards_left_in_deck
        self.discard_pile = [] # pretty sure this will fill up with `Card()`s, rather than just `Value()` flags.
        self.stacks = [Stack(S) for S in self.suits]
        self.clue_tokens = 8
        self.lives = 3
        #print(self.deck)
        self.current_player = 0 # this is potentially confusing.
        # As a convention writter you should always assume that you, the current player, is player 0
        # The next player is player 1, and the player after that is player 2 and so on.
        # This value is used by the game engine to keep track of which hands to show to the convention at any given time
        # and should not be accessed directly.
        self.number_of_players = number_of_players
        if 1 <= number_of_players <= 3:
            self.hand_size = 5
        elif 4 <= number_of_players <= 5:
            self.hand_size = 4
        else:
            raise ValueError("Invalid hand size")
        self.card = Cards()
        self.card.cards = [[Card(self.deck.pop()) for _ in range(self.hand_size)] for _ in range(number_of_players)]

    def play_card(self, card_index):  # plays current player's ith card
        if Game.debug: print(f"Playing {str(self.card[0][card_index])}.")
        playable_card = self.card[0].pop(card_index)
        if len(self.deck):
            self.card[0].insert(0, Card(self.deck.pop()))
        elif self.cards_left_in_deck:
            self.cards_left_in_deck = False
        card_fits = False
        for S in self.stacks:
            if S.fits(playable_card):
                card_fits = True
                S.play()
        if card_fits:
            if Game.debug: print("Yay, a card was played correctly.")
            pass
        else:
            if Game.debug: print("Oh dear, a card was played incorrectly and a life was lost.")
            self.lives -= 1


    def discard(self, card_index):  # discards current player's ith card
        if self.clue_tokens == 8:
            return False
        if Game.debug: print(f"Discarding {str(self.card[0][card_index])}.")
        #print(list(self.card[0]))
        self.discard_pile.append(self.card[0].pop(card_index))
        self.clue_tokens += 1
        if len(self.deck):
            self.card[0].insert(0, Card(self.deck.pop()))
        elif self.cards_left_in_deck:
            self.cards_left_in_deck = False
        #print(list(self.card[0]))
        return True

    def clue(self, player_index, clue):  # tries to give clue to given player. Returns True for success and False for failure
        could_give_clue = False
        if self.clue_tokens == 0:
            return False
        for c in self.card[player_index]:
            if clue in (Value() - c).data:
                could_give_clue = True
                c += Touched(clue)
        if could_give_clue:
            if Game.debug: print(f"Giving player {player_index + 1} a clue of {clue}.")
            self.clue_tokens -= 1
        return could_give_clue

    def display_hands(self):
        print(str(self.card))

    def display_all_flags(self):
        print(repr(self.card))

    def game_running(self):
        if self.lives == 0:
            #print(f"Ran out of lives!")
            return False
        if not self.cards_left_in_deck:
            if self.turns_remaining > 0:
                self.turns_remaining -= 1
                return True
            #print("Ran out of turns!")
            return False
        return True

    def get_score(self):
        return sum(map(lambda x: x.rank, self.stacks))

    def move_hands(self):
        self.card.move_cards()

    def game_status(self):
        print(f"Clues: {self.clue_tokens}, Lives: {self.lives}, Score: {self.get_score()}, Stacks: {self.stacks}.")

    def make_move(self):
        pass

    def update(self):
        pass