from GameLogic import Game, Touched, Value
from CustomFlags import Immediately_Playable, Chop, Chop_Moved

class v1_0(Game):
    version = "v1.0"

    def play_immediately_playable_card(self):
        for index, c in enumerate(self.card[0]):
            if c == Immediately_Playable():
                self.play_card(index)
                return True # success
        return False # failure

    def give_play_clue(self):
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
        return False # tried to give clues but failed for some reason, possibly couldn't do so without cluing other cards.

    def discard_final_card(self):
        if self.clue_tokens < 8:
            self.discard(-1)
            return True
        return False

    def clue_prev_player_final_card(self):
        v = Value() - self.card[-1][-1]
        if self.clue(-1, v.data[1]):
            return True
        return False

    def make_move(self):
        if self.play_immediately_playable_card(): return True
        if self.give_play_clue(): return True
        if self.discard_final_card(): return True
        if self.clue_prev_player_final_card(): return True
        print("Couldn't find an action to take")
        return False

    def update(self):
        for h in range(self.number_of_players):
            if any(1 for c in self.card[h] if c == Touched() and c!= Immediately_Playable()):
                for c in self.card[h]:
                    if c == Touched() and c!= Immediately_Playable():
                        c + Immediately_Playable()
                        break
        for h in range(self.number_of_players):
            for c in self.card[h]:
                if c == Touched():
                    c - Touched()


class v1_1(Game):
    version = "v1.1"
    def player_has_playable_cards(self, player):
        for index, c in enumerate(self.card[player]):
            if c == Immediately_Playable():
                return True
        return False

    def give_save_clue_to_player(self, player):
        return False

    def play_immediately_playable_card(self):
        for index, c in enumerate(self.card[0]):
            if c == Immediately_Playable():
                self.play_card(index)
                return True # success
        return False # failure

    def give_save_clue(self): # to anyone, starting with player 1 and working round
        for h in range(1, self.number_of_players):
            if self.give_save_clue_to_player(h): return True
        return False

    def get_critical_card_values(self):
        all_card_values = [Value(S+R) for S in self.suits for R in self.ranks]
        for c in self.discard_pile:
            all_card_values.remove(c)
        possible_critical_card_values = []
        non_critical_card_values = []
        for c in all_card_values:
            if c not in possible_critical_card_values:
                possible_critical_card_values.append(c)
            else:
                non_critical_card_values.append(c)
        for c in non_critical_card_values:
            while c in possible_critical_card_values:
                possible_critical_card_values.remove(c)
        # possible_critical_card_values has the value of any card for which
        # precisely one copy of that card remains in play
        # now need to remove useless cards (e.g. G3 if all three G1s have been discarded)
        dead_card_values = []
        for cd in self.discard_pile:
            if cd not in all_card_values and cd not in dead_card_values:
                dead_card_values.append(Value() - cd)
        #print(dead_card_values)
        #print(possible_critical_card_values)
        for dead_card_value in dead_card_values:
            suit, rank_str = dead_card_value.data[0], dead_card_value.data[1]
            for rank in range(int(rank_str), 5+1):
                if (v := Value(suit + str(rank))) in possible_critical_card_values:
                    possible_critical_card_values.remove(v)
        critical_card_values = possible_critical_card_values
        return critical_card_values

    def could_be_save_clue(self, player, clue): # still working on this, needs finishing.
        for index, c in enumerate(self.card[player]):
            if c == Chop(): # found the chop card
                v = Value() - c
                if clue in v.data: # this clue will touch the chop card
                    critical_card_values = self.get_critical_card_values()
                    for v in critical_card_values:
                        if clue in v.data: # this clue could be talking about a critical card, so this could be a save clue
                            return True

        return False

    def give_play_clue_not_save(self):
        return False

    def discard_chop_card(self):
        for index, c in enumerate(self.card[0]):
            if c == Chop():
                return self.discard(index)
        return False

    def clue_prev_player_rank_final_card(self):
        v = Value() - self.card[-1][-1]
        if self.clue(-1, v.data[1]):
            return True
        return False

    def play_final_card(self):
        return self.play_card(-1)

    def make_move(self):
        if self.player_has_playable_cards(1) and self.give_save_clue_to_player(1): return True
        if self.play_immediately_playable_card(): return True
        if self.give_save_clue(): return True
        if self.give_play_clue_not_save(): return True
        if self.discard_chop_card(): return True
        if self.clue_prev_player_rank_final_card(): return True
        if self.play_final_card(): return True
        print("Couldn't find any action to take")
        return False
    def update(self):
        pass