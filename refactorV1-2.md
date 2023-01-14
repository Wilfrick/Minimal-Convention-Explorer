# Refactoring Conventions

As expected, implementing some of my ideas for a simple convention has lead to more complex ideas that I would like to implament. However, at the moment (versions 1.0 and 1.1) there is a monolithic chunck of code in each class called `make_move`, which contains all of the logic for deciding which action to take. I have already broken that problem down into smaller chunks, but what I'd really like is to have is a way to reuse some of those chunks in later conventions.

Consider the following setup: Each unit of convention (ucon) should define the following:
1. A list of flags that will be accessed
2. A list of flags that will be modified
3. A `make_move` function, which may return no action
4. An `update` function for keeping the flags up to date

An ordered list of multiple 'child' ucons can be combined into a single, larger 'parent' ucon by defining:
1. The list of accessed flags is the union of all flags accessed by any child ucon
2. The list of modified flags is the union of all flags modified by any child ucon
3. The `make_move` function can be defined by iterating through the `make_move` functions of each child in order and returning the first definite action, defaulting to returning no action. This definition means that child ucons earlier in the order have a higher priority, but later ucons can still choose actions if nothing more important needs to happen
4. The `update` function similarly iterates through the `update` function for each child and runs those in series, again with an implied priority.

## Terminology
In order to get some information out of the system, at least one ucon must be able to read the `Value` flag. This is the only flag that is not global information and also is the only read only flag. I think it could make sense to have a specific work for ucons that use the `Value` flag, so I will say that any such ucon is 'opaque' - it's could use information not available to everyone and so it's actions can't be predicted. In contrast, a ucon that does not reference `Value` flags can be simulated using only global knowlegde, so it's actions are clear and we call it 'transparent'.
If multiple child ucons are combined into a single parent ucon then by default if any of the children are opaque the parent is too and the parent can only be tranparent if all of its children are as well. I'll note here that it is technically possible that the interactions between different children can cancel out or negate the effects of some or all of the opaque children, so a parent with some (or maybe even all) opaque children could be shown to be functionally transparent. 

## File format
For now I'll keep each ucon as a single class. In due course they might become interactive command line scripts or maybe even networked chunks of code that can respond to queries, but I want to keep things as simple as I can for the moment. Each ucon should have the following format
```python3
#<ucons>.py
class <ucon name>:
    flags_accessed = [] # a list of uuids, which are sha256 hashes
    flags_modified = [] # a list of uuids, which are sha256 hashes
    def make_move(self):
        return False # means no action taken
        # could also call self.clue(<hand index>, <clue>),
        # self.play_card(<card index>)
        # or self.discard(<card index>)
        # and each of these methods returns True on success and False on failure

    def update(self):
        pass # is allowed to modify flags using self.card[h][n] as discussed below.
```
In order for `make_move` and `update` to be able to access the game state, the variable `self` has several attributes that store this data. Many of these are self explanitory and can be found in the `__init__` method of `Game` class in `GameLogic.py`, but some of the more complex structures are given more detail below:
- `self.cards[<hand index>][<card index>]` returns an instance of `Card`, which has special behaviour with `==`, `+` and `-`. Please take head that `-` is especially weird, having different definitions depending on context.
  - To explain, consider `c = self.cards[0][0]`. `c` is now the `Card` representing the current player's frontmost card.
  - `c + Flag("I'm playable")` adds the given flag to the card's internal list of flags, assuming there isn't already that flag present on this card (if there is then this action is ignored). (N.B. flag equality has also been overwritten, but by default two different instances of a given flag are considered equal unless they have explicitly both been given different data, in which case they are considered not equal)
  - `c - Flag("I'm playable")` removes the given flag from the card's internal list of flags, if the card currently contains a flag considered equal to this one. This can be useful to remove flags that you don't quite fully know. E.g. `c - Touched()` removes any `Touched(5)` flag from the card (as well as any other `Touched()` flag), because `Touched()` defines no explicit additonal data. If no such equal flag exists for this card then nothing happens.
  - `c == Flag("I'm playable")` returns `True` if the card's internal list of flags contains a flag considered equal to the given flag and `false` otherwise. This is intended to make code more readable.
  - `Flag("I'm playable") - c` returns the first flag (from the card's internal list of flags) that is considered equal to the given flag. This allows you to query the data in that flag and make decisions based on it. For example, `v = Value() - c` finds and stores the `Value()` flag for the given card, and then the data inside that flag can be accessed and used (e.g. with `suit, rank = v.data[0], v.data[1]`). In this particular case `c` is a card in our hand, so we would be accessing the value of a card in our hand, which should be avoided if you want to play the game fairly, but obviously `c` could be any card and this would still work.
- `self.stacks` is a list of `Stack`s, each of which has a `fits` method. This method returns a boolean describing whether the given card would be the next card for that stack. As an example, a card `c` is playable right now iff `any(1 for S in self.stacks if S.fits(c)))` is true.

## Next steps
I think all that's left to do is to refactor one of the existing conventions (probably v1.0 because I know that that one works) and see if this system works. The goal is to make reusing small, independent chunks of convention possible, so let's see how well this does that.