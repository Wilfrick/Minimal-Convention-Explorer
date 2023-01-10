class Card_View:
    def __init__(self, hand):
        self.hand = hand
        self.sanitised_view = [copy(c) - Value() for c in self.hand]
        self.removed_flags = [Value() - copy(c) for c in self.hand]

    def __getitem__(self, item):
        return self.sanitised_view[item]

    def __setitem__(self, key, value):
        if self.removed_flags[key]:
            self.hand[key] = value + self.removed_flags[key]
        else: self.hand[key] = value
        #self.__init__(self.hand) not sure if needed.

    def __delitem__(self, key):
        del self.sanitised_view[key]

    def __str__(self):
        return str(self.sanitised_view)

    __repr__ = __str__

class v1_0(Game):
    version = "v1.0"
    def make_move_old(self):
        for index, c in enumerate(self.card[0]):
            if c == Immediately_Playable():
                self.play_card(index)
                return True
        if self.clue_tokens > 0:
            for h in range(1, self.number_of_players):
                for n in range(len(self.card[h])):
                    c = self.card[h][n]
                    if c != Immediately_Playable():
                        could_be_played_immediately = False
                        for S in self.stacks:
                            if S.fits(c):
                                could_be_played_immediately = True
                        if could_be_played_immediately:
                            v = Value() - c
                            suit, rank = v.data[0], v.data[1]
                            could_give_suit_clue = True
                            could_give_rank_clue = True
                            for i in range(n):
                                value_of_earlier_card_in_hand = Value() - self.card[h][i]
                                suit_of_earlier_card_in_hand, rank_of_earlier_card_in_hand = value_of_earlier_card_in_hand.data[0], value_of_earlier_card_in_hand.data[1]
                                if suit_of_earlier_card_in_hand == suit:
                                    could_give_suit_clue = False
                                if rank_of_earlier_card_in_hand == rank:
                                    could_give_rank_clue = False
                            if could_give_suit_clue:
                                if self.clue(h, suit):
                                    return True
                            if could_give_rank_clue:
                                if self.clue(h, rank):
                                    return True
                            # tried to give clues but failed for some reason, possibly couldn't do so without cluing other cards.
        if self.clue_tokens < 8:
            self.discard(-1)
            return True

        v = Value() - self.card[-1][-1]

        if self.clue(-1, v.data[1]):
            return True
        print("Something has gone wrong and I was unable to select a move")
        return False