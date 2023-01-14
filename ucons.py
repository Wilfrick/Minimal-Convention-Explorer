from inspect import getsource
from hashlib import sha256

class ucon:
    def __init__(self, name = "ucon", children = None):
        self.name = name
        self.flags_accessed = [] # a list of uuids, which are sha256 hashes
        self.flags_modified = [] # a list of uuids, which are sha256 hashes
        self.isparent = False
        self.transparent = False # opaque by default
        #print(f"{self.name}: {isinstance(children, (list, tuple))}")
        #if isinstance(children, (list, tuple)):
            #print(f"{self.name}: {isinstance(children, (list, tuple))}, {len(children)}")
        #if isinstance(children, (list, tuple)) and len(children):
            #print(f"{self.name}: {isinstance(children, (list, tuple))}, {len(children)}, {all(isinstance(c, ucon) for c in children)}")
        if isinstance(children, (list, tuple)) and len(children) and all(isinstance(c, ucon) for c in children):
            self.children = children
            self.isparent = True
            self.transparent = all(c.transparent for c in self.children) # default opacity behaviour
            self.flags_accessed = list(set(sum([c.flags_accessed for c in self.children], start=[])))
            self.flags_modified = list(set(sum([c.flags_modified for c in self.children], start=[])))

    @property
    def uuid(self):
        return sha256(getsource(self.__class__).encode()).hexdigest()

    def make_move(self, game):
        if self.isparent:
            for c in self.children:
                if c.make_move(game):
                    return True
            return False
        return False  # means no action taken
        # could also call self.clue(<hand index>, <clue>),
        # self.play_card(<card index>)
        # or self.discard(<card index>)
        # and each of these methods returns True on success and False on failure

    def update(self, game):
        if self.isparent:
            for c in self.children:
                c.update(game)
        else:
            pass  # don't do anything
        # is allowed to modify flags using self.card[h][n] as discussed below.

    def clear_flag(self, game, flag): # included for convenience
        for h in range(game.number_of_players):
            for c in game.card[h]:
                c - flag



    def __str__(self):
        if not self.isparent:
            return self.name
        else:
            bk = "\n"
            tb = "\t"
            return f"{self.name}:{bk.join(tb.join([''] + str(c).splitlines()) for c in self.children)}"
        # may need a little tweeking to look right


import CustomFlags, GameLogic
class play_immediately_playable_card(ucon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, name = "play_immediately_playable_card", **kwargs)
        self.flags_accessed = [CustomFlags.Immediately_Playable().uuid]
        self.flags_modified = [CustomFlags.Immediately_Playable().uuid]

    def make_move(self, game):
        for index, c in enumerate(game.card[0]): # look through cards in my hand
            if c == CustomFlags.Immediately_Playable():
                game.play_card(index)
                return True # success
        return False # failure

    # no need to overwrite `update` as we don't need to update anything

class discard_last_card(ucon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, name = "discard_last_card", **kwargs)
        self.flags_accessed = []
        self.flags_modified = []

    def make_move(self, game):
        #print("discarding last card")
        if game.clue_tokens < 8:
            game.discard(-1)
            return True
        return False

class clue_prev_player_final_card(ucon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, name = "clue_prev_player_final_card", **kwargs)
        self.flags_accessed = [GameLogic.Value().uuid]
        self.flags_modified = [GameLogic.Touched().uuid]

    def make_move(self, game):
        #print("giving a bad clue")
        v = GameLogic.Value() - game.card[-1][-1]
        if game.clue(-1, v.data[1]):
            return True
        return False

class front_most_touched_is_immediately_playable(ucon):
    def __init__(self):
        super().__init__(name = "front_most_newly_clued_is_immediately_playable")
        self.flags_accessed = [GameLogic.Touched().uuid, CustomFlags.Immediately_Playable().uuid]
        self.flags_modified = [CustomFlags.Immediately_Playable().uuid]

    # no need to overwrite make_move as this doesn't directily make any moves
    def update(self, game):
        for h in range(game.number_of_players):
            if any(1 for c in game.card[h] if c == GameLogic.Touched() and c!= CustomFlags.Immediately_Playable()):
                for c in game.card[h]:
                    if c == GameLogic.Touched() and c!= CustomFlags.Immediately_Playable():
                        c + CustomFlags.Immediately_Playable()
                        break
        self.clear_flag(game, GameLogic.Touched())

class delete_touches(ucon):
    def __init__(self):
        super().__init__(name = "delete_touches")
        self.flags_accessed = [GameLogic.Touched().uuid]
        self.flags_modified = [GameLogic.Touched().uuid]

    def update(self, game):
        for h in range(game.number_of_players):
            for c in game.card[h]:
                if c == GameLogic.Touched():
                    c - GameLogic.Touched()

class give_play_clue_as_front_most_touched_card_ucon(ucon):
    def __init__(self):
        super().__init__(name = "give_play_clue_dependent_ucon")
        self.flags_accessed = [CustomFlags.Immediately_Playable().uuid, GameLogic.Value().uuid]
        self.flags_modified = []

    def make_move(self, game):
        if game.clue_tokens > 0:
            for h in range(1, game.number_of_players):
                for n in range(len(game.card[h])):
                    c = game.card[h][n]
                    if c != CustomFlags.Immediately_Playable():
                        could_be_played_immediately = False
                        for S in game.stacks:
                            if S.fits(c):
                                could_be_played_immediately = True
                        if could_be_played_immediately:
                            v = GameLogic.Value() - c
                            suit, rank = v.data[0], v.data[1]
                            could_give_suit_clue = True
                            could_give_rank_clue = True
                            for i in range(n):
                                value_of_earlier_card_in_hand = GameLogic.Value() - game.card[h][i]
                                suit_of_earlier_card_in_hand, rank_of_earlier_card_in_hand = value_of_earlier_card_in_hand.data[0], value_of_earlier_card_in_hand.data[1]
                                if suit_of_earlier_card_in_hand == suit:
                                    could_give_suit_clue = False
                                if rank_of_earlier_card_in_hand == rank:
                                    could_give_rank_clue = False
                            if could_give_suit_clue:
                                if game.clue(h, suit):
                                    return True
                            if could_give_rank_clue:
                                if game.clue(h, rank):
                                    return True
        #print("Tried but failed to give a play clue")
        return False # tried to give clues but failed for some reason, possibly couldn't do so without cluing other cards.

class front_most_touched_card_can_and_should_be_played(ucon):
    def __init__(self):
        super().__init__(name = "front_most_touched_card_can_and_should_be_played",
                         children = [play_immediately_playable_card(),
                                     give_play_clue_as_front_most_touched_card_ucon(),
                                     front_most_touched_is_immediately_playable(),
                                     delete_touches()])

class do_something(ucon):
    def __init__(self):
        super().__init__(name = "do_something",
                         children=[discard_last_card(),
                                   clue_prev_player_final_card()])

class v1_0(ucon):
    def __init__(self):
        super().__init__(name = "v1.0", children=[front_most_touched_card_can_and_should_be_played(),
                                                  do_something()])

class find_and_mark_critical_cards_not_fives(ucon):
    def __init__(self):
        super().__init__(name = "find_and_mark_critical_cards")
        self.flags_accessed = [GameLogic.Value().uuid]
        self.flags_modified = [CustomFlags.Critical().uuid]

    def make_move(self, game):
        for h in range(1, game.number_of_players):
            for c in game.card[h]:
                v = GameLogic.Value() - c
                count = 0
                for discarded_card in game.discard_pile:
                    if discarded_card == v:
                        count += 1
                critical = False
                if int(v.data[1]) == 1 and count == 2:
                    critical = True
                elif 1 < int(v.data[1]) < 5 and count == 1:
                    critical = True
                if critical:
                    c + CustomFlags.Critical()
        return False # don't do anything

    def update(self, game): # clears Critical flags
        for h in range(1, game.number_of_players):
            for c in game.card[h]:
                c - CustomFlags.Critical()

class give_save_clue_to_critical_cards(ucon):
    def __init__(self):
        super().__init__(name = "give_save_clue")
        self.flags_accessed = [CustomFlags.Critical().uuid, GameLogic.Value().uuid]
        self.flags_modified = [GameLogic.Touched().uuid]

    def make_move(self, game):
        for h in range(1, game.number_of_players):
            for c in reversed(game.card[h]):
                if c == CustomFlags.Critical() and c != CustomFlags.Chop_Moved(): # if we find a critical unsaved card
                    v = GameLogic.Value() - c
                    if game.clue(h, v.data[1]): # give save clue with number, technically doesn't matter
                        #print("Giving save clue")
                        return True
                    break
        return False

    def update(self, game):
        for h in range(1, game.number_of_players):
            if any(1 for c in game.card[h] if c == GameLogic.Touched() and c == CustomFlags.Critical() and c != CustomFlags.Chop_Moved()):
                # if a new critical card was touched in hand that was not already saved
                for c in reversed(game.card[h]):
                    if c == GameLogic.Touched() and c == CustomFlags.Critical() and c != CustomFlags.Chop_Moved():
                        c + CustomFlags.Chop_Moved()
                    break
                self.clear_flag(game, GameLogic.Touched()) # use up this clue if it really was a save clue
        self.clear_flag(game, CustomFlags.Critical())


class give_save_clue(ucon):
    def __init__(self):
        super().__init__(name = "give_save_clue", children=[find_and_mark_critical_cards_not_fives(),
                                                            give_save_clue_to_critical_cards()])

class give_play_clue_not_accidentally_save_clue(ucon):
    def __init__(self):
        super().__init__(name="give_play_clue_not_accidentally_save_clue")
        self.flags_accessed = [CustomFlags.Immediately_Playable().uuid, GameLogic.Value().uuid, CustomFlags.Critical().uuid]
        self.flags_modified = []

    def make_move(self, game):
        if game.clue_tokens > 0:
            for h in range(1, game.number_of_players):
                for n in range(len(game.card[h])):
                    c = game.card[h][n]
                    if c != CustomFlags.Immediately_Playable():
                        could_be_played_immediately = False
                        for S in game.stacks:
                            if S.fits(c):
                                could_be_played_immediately = True
                        if could_be_played_immediately:
                            v = GameLogic.Value() - c
                            suit, rank = v.data[0], v.data[1]
                            could_give_suit_clue = True
                            could_give_rank_clue = True
                            for i in range(n): # check that this is the earliest card we will touch
                                value_of_earlier_card_in_hand = GameLogic.Value() - game.card[h][i]
                                suit_of_earlier_card_in_hand, rank_of_earlier_card_in_hand = \
                                value_of_earlier_card_in_hand.data[0], value_of_earlier_card_in_hand.data[1]
                                if suit_of_earlier_card_in_hand == suit:
                                    could_give_suit_clue = False
                                if rank_of_earlier_card_in_hand == rank:
                                    could_give_rank_clue = False
                            for i in range(n, game.hand_size, -1): # check this isn't accidentally a save clue
                                c = game.card[h][i]
                                if c == CustomFlags.Critical() and c != CustomFlags.Chop_Moved():
                                    v = GameLogic.Value() - c
                                    suit_of_potentially_saveable_card, rank_of_potentially_saveable_card = v.data[0], v.data[1]
                                    if suit == suit_of_potentially_saveable_card:
                                        could_give_suit_clue = False
                                    if rank == rank_of_potentially_saveable_card:
                                        could_give_rank_clue = False
                                break
                            if could_give_suit_clue:
                                if game.clue(h, suit):
                                    return True
                            if could_give_rank_clue:
                                if game.clue(h, rank):
                                    return True
        # print("Tried but failed to give a play clue")
        return False  # tried to give clues but failed for some reason, possibly couldn't do so without cluing other cards.


class discard_last_non_chop_moved_card(ucon):
    def __init__(self):
        super().__init__(name = "discard_last_non_chop_moved_card")
        self.flags_accessed = [CustomFlags.Chop_Moved().uuid]

    def make_move(self, game):
        for card_index, c in reversed(list(enumerate(game.card[0]))):
            if c != CustomFlags.Chop_Moved():
                return game.discard(card_index)
        return False

class v1_1(ucon):
    def __init__(self):
        super().__init__(name = "v1.1",
                         children = [
                                     play_immediately_playable_card(),
                             #give_save_clue(),
                                     give_play_clue_not_accidentally_save_clue(),

                                     front_most_touched_is_immediately_playable(),

                                     discard_last_non_chop_moved_card(),
                                     #give_save_clue(),
                                     do_something(),
                                     ])

if __name__ == "__main__":
    u = ucon(name = "hi there")
    b = do_something()
    v = v1_0()
    print(u.name)
    print(b.name)
    print(v.name)