def run_trial(version, number_of_players):
    G = version(number_of_players)
    while G.game_running():
        G.make_move()
        G.update()
        G.move_hands()
    return G.get_score()

from GameLogic import Game
def run_trail_2(convention, number_of_players):
    G = Game(number_of_players)
    while G.game_running():
        if not convention.make_move(G):
            print("couldn't find a move")
        convention.update(G)
        G.move_hands()
    return G.get_score()

if __name__ == "__main__":
    from ucons import v1_0, do_something, clue_prev_player_final_card
    import Stats
    N = 1000
    score_bins = [0 for _ in range(26)]
    conv = v1_0()
    scores = [run_trail_2(conv, 3) for _ in range(N)]
    for score in scores:
        score_bins[score] += 1

    print(score_bins)
    print(f"Played {sum(score_bins)} games with {conv.name}, with an average of {Stats.mean(score_bins)} with 90% of the games scoring between {Stats.percentile(score_bins, 5)} and {Stats.percentile(score_bins, 95)}.")
