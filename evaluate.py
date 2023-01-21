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

        #G.display_all_flags()
        convention.update(G)
        #G.display_all_flags()
        G.move_hands()
        #print("")
    return G.get_score()

if __name__ == "__main__":
    from ucons import cheat_ucon_v1, cheat_ucon_v2, cheat_ucon_v3
    import Stats
    N = 10000
    cutoff = 17  # 17 is best for 3 player
    score_bins = [0 for _ in range(26)]
    conv = cheat_ucon_v3(cutoff)
    scores = [run_trail_2(conv, 3) for _ in range(N)]
    for score in scores:
        score_bins[score] += 1

    print(score_bins)
    print(f"Played {sum(score_bins)} games with {conv.name}, with an average of {Stats.mean(score_bins)} with 90% of the games scoring between {Stats.percentile(score_bins, 5)} and {Stats.percentile(score_bins, 95)}.")
