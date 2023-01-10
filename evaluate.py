def run_trial(version, number_of_players):
    G = version(number_of_players)
    while G.game_running():
        G.make_move()
        G.update()
        G.move_hands()
    return G.get_score()

if __name__ == "__main__":
    from Conventions import v1_0
    import Stats
    N = 1000
    score_bins = [0 for _ in range(26)]
    scores = [run_trial(v1_0, 3) for _ in range(N)]
    for score in scores:
        score_bins[score] += 1

    print(score_bins)
    print(f"Played {sum(score_bins)} games with {v1_0.version}, with an average of {Stats.mean(score_bins)} with 90% of the games scoring between {Stats.percentile(score_bins, 5)} and {Stats.percentile(score_bins, 95)}.")
