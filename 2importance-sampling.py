# Compute the frequency of each number in the historical data.

# Convert the frequencies into a probability distribution (this becomes our "importance" distribution).

# Sample numbers based on that distribution rather than uniformly at random.

import random
import json
from collections import Counter

def load_lottery_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def get_filtered_draws(data, draw_time):
    return [entry for entry in data if entry['time'].lower() == draw_time]

def build_importance_distribution(draws):
    # Flatten all numbers into one list
    all_numbers = [num for entry in draws for num in entry['numbers']]
    
    # Count frequency
    frequency = Counter(all_numbers)
    
    # Normalize frequencies to probabilities
    total = sum(frequency.values())
    probability_distribution = {num: count / total for num, count in frequency.items()}
    
    return probability_distribution

def importance_sample(prob_dist, k=4):
    numbers = list(prob_dist.keys())
    weights = list(prob_dist.values())
    
    # Sample 4 unique numbers based on importance weights
    sampled = set()
    while len(sampled) < k:
        sampled.add(random.choices(numbers, weights=weights, k=1)[0])
    return sorted(sampled)

def main():
    file_path = "merged_uk_49s_results.json"
    lottery_data = load_lottery_data(file_path)

    # User input
    time_filter = input("Enter draw time (lunchtime/teatime): ").strip().lower()
    num_predictions = int(input("How many 4-number predictions would you like to generate? "))

    # Filter dataset
    filtered_draws = get_filtered_draws(lottery_data, time_filter)

    # Build importance distribution
    importance_dist = build_importance_distribution(filtered_draws)

    # Generate predictions
    print(f"\n🎯 Predicted {num_predictions} sets of 4 numbers (Importance Sampling):")
    for _ in range(num_predictions):
        print(importance_sample(importance_dist))

if __name__ == "__main__":
    main()
