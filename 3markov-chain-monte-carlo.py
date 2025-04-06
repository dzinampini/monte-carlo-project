# Create a Markov transition matrix for individual numbers (i.e., if 8 appears often after 7, the transition probability from 7 → 8 is high).

# Start from a random number or the most frequent one.

# Use MCMC to sample 4-number sequences based on the learned transition probabilities.

import random
import json
from collections import defaultdict, Counter

def load_lottery_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def get_filtered_draws(data, draw_time):
    return [entry for entry in data if entry['time'].lower() == draw_time]

def build_markov_chain(draws):
    transitions = defaultdict(Counter)

    # For each draw, record number-to-number transitions
    for entry in draws:
        numbers = sorted(entry['numbers'])  # sort to simulate a sequence
        for i in range(len(numbers) - 1):
            transitions[numbers[i]][numbers[i + 1]] += 1

    # Normalize transitions to probabilities
    markov_chain = {}
    for current, next_counts in transitions.items():
        total = sum(next_counts.values())
        markov_chain[current] = {nxt: count / total for nxt, count in next_counts.items()}

    return markov_chain

def mcmc_sample(chain, sequence_length=4):
    # Start from a random state
    current = random.choice(list(chain.keys()))
    sequence = [current]

    while len(sequence) < sequence_length:
        next_states = chain.get(current, {})
        if not next_states:
            # If dead end, restart from another random state
            current = random.choice(list(chain.keys()))
            continue

        next_numbers = list(next_states.keys())
        probs = list(next_states.values())

        current = random.choices(next_numbers, weights=probs, k=1)[0]

        # Avoid repeating numbers
        if current not in sequence:
            sequence.append(current)

    return sorted(sequence)

def main():
    file_path = "merged_uk_49s_results.json"
    lottery_data = load_lottery_data(file_path)

    # User input
    time_filter = input("Enter draw time (lunchtime/teatime): ").strip().lower()
    num_predictions = int(input("How many 4-number predictions would you like to generate? "))

    # Filter draws
    dataset = get_filtered_draws(lottery_data, time_filter)

    # print(dataset)

    # Build Markov chain
    markov_chain = build_markov_chain(dataset)

    # Generate predictions
    print(f"\n🎯 Predicted {num_predictions} sets of 4 numbers using MCMC:")
    for _ in range(num_predictions):
        print(mcmc_sample(markov_chain))

if __name__ == "__main__":
    main()
