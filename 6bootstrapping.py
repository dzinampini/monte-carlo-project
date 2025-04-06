# Random resampling with replacement from historical draws.

# Generating multiple synthetic datasets (bootstrap samples).

# Estimating a statistic (like frequency) across these samples.

# Using that statistic to make predictions (e.g., which numbers appear most frequently across resamples).

import random
import json
from collections import Counter

def load_lottery_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def get_filtered_draws(data, draw_time):
    return [entry for entry in data if entry['time'].lower() == draw_time]

def bootstrap_resample(draws, n_samples=1000):
    """Generate bootstrap samples (with replacement)."""
    return [random.choice(draws)['numbers'] for _ in range(n_samples)]

def aggregate_frequencies(bootstrap_samples):
    """Count frequency of all numbers across samples."""
    all_numbers = [num for sample in bootstrap_samples for num in sample]
    return Counter(all_numbers)

def generate_predictions(freq_counter, num_predictions=5, sequence_length=4):
    """Use top frequent numbers to form predictions."""
    top_numbers = [num for num, _ in freq_counter.most_common(20)]  # top 20 numbers
    predictions = []
    for _ in range(num_predictions):
        predictions.append(sorted(random.sample(top_numbers, sequence_length)))
    return predictions

def bootstrap_predict(draws, num_predictions=5, sequence_length=4, bootstrap_iterations=1000):
    samples = bootstrap_resample(draws, n_samples=bootstrap_iterations)
    freq_counter = aggregate_frequencies(samples)
    return generate_predictions(freq_counter, num_predictions, sequence_length)

def main():
    file_path = "merged_uk_49s_results.json"
    lottery_data = load_lottery_data(file_path)

    # User input
    time_filter = input("Enter draw time (lunchtime/teatime): ").strip().lower()
    num_predictions = int(input("How many 4-number predictions would you like to generate? "))

    dataset = get_filtered_draws(lottery_data, time_filter)

    print(f"\n🔄 {num_predictions} Predictions using Bootstrapping:")
    predictions = bootstrap_predict(dataset, num_predictions=num_predictions)
    for pred in predictions:
        print(pred)

if __name__ == "__main__":
    main()
