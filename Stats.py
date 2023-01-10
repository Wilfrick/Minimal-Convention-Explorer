def mean(score_bins):
    return sum(index*value for index, value in enumerate(score_bins)) / sum(score_bins)

def percentile(score_bins, percentile):
    fraction = percentile / 100
    target_index = int(sum(score_bins)*fraction)
    for index, value in enumerate(score_bins):
        if target_index > value:
            target_index -= value
            continue
        # target_index <= value at this point
        return index