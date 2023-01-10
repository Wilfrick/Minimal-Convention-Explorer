from Conventions import v1_1


G = v1_1(3)
for _ in range(10):
    G.clue_tokens = 0
    G.discard(-1)
    G.move_hands()
print(G.deck)
print(G.discard_pile)
print(G.get_critical_card_values())

