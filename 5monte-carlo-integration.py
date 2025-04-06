# Monte Carlo Integration estimates an expected value of a function by sampling random inputs. In our context:

# Let the function 
# 𝑓
# (
# 𝑥
# )
# f(x) be the likelihood of a 4-number set occurring, based on past draws.

# We sample many 4-number sets, evaluate them using 
# 𝑓
# (
# 𝑥
# )
# f(x), and take the top ones.

# We’ll:

# Define a probability density function from past draw frequencies.

# Use random sampling to generate many 4-number combinations.

# Use those to estimate expected likelihood and choose the top ones.

import random
import json
from collections import Counter

def load_lottery_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def get_filtered_draws(data, draw_time):
    return [entry for entry in data if entry['time'].lower() == draw_time]

def compute_number_frequencies(draws):
    all_numbers = [num for entry in draws for num in entry['numbers']]
    frequency = Counter(all_numbers)
    total = sum(frequency.values())
    return {num: freq / total for num, freq in frequency.items()}

def generate_random_sequence(number_pool, k=4):
    return sorted(random.sample(number_pool, k))

def estimate_expectation(sequences, freq_dist):
    estimates = {}
    for seq in sequences:
        prob = sum([freq_dist.get(num, 0.0001) for num in seq])
        estimates[tuple(seq)] = prob
    return estimates

def monte_carlo_integration_predict(draws, num_predictions=5, num_samples=1000, sequence_length=4):
    freq_dist = compute_number_frequencies(draws)
    number_pool = list(freq_dist.keys())

    # Step 1: Randomly sample 4-number sets
    random_sequences = [generate_random_sequence(number_pool, sequence_length) for _ in range(num_samples)]

    # Step 2: Estimate expected value (likelihood)
    estimates = estimate_expectation(random_sequences, freq_dist)

    # Step 3: Select top N sequences with highest estimated value
    top_sequences = sorted(estimates.items(), key=lambda x: x[1], reverse=True)[:num_predictions]
    return [list(seq) for seq, _ in top_sequences]

def main():
    file_path = "merged_uk_49s_results.json"
    lottery_data = load_lottery_data(file_path)

    # User input
    time_filter = input("Enter draw time (lunchtime/teatime): ").strip().lower()
    num_predictions = int(input("How many 4-number predictions would you like to generate? "))

    dataset = get_filtered_draws(lottery_data, time_filter)

    print(f"\n🎲 {num_predictions} Predictions using Monte Carlo Integration:")
    predictions = monte_carlo_integration_predict(dataset, num_predictions=num_predictions)
    for pred in predictions:
        print(pred)

if __name__ == "__main__":
    main()
