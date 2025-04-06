# 🧠 SMC in Lottery Context:
# Each particle:

# Represents a 4-number sequence.

# Has a weight based on how similar it is to recent real draws.

# Is resampled at each iteration to favor high-weighted particles.

# We’ll:

# Initialize a population of random particles (number sequences).

# Define a likelihood function — how likely is a sequence, given historical data (e.g., based on number frequencies).

# At each step (iteration), sample particles based on weights and mutate them slightly.

# Return top-k predictions. 

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

def initialize_particles(num_particles, number_pool, sequence_length=4):
    particles = []
    for _ in range(num_particles):
        particles.append(sorted(random.sample(number_pool, sequence_length)))
    return particles

def likelihood(sequence, freq_dist):
    # Simple likelihood: sum of individual number probabilities
    return sum([freq_dist.get(n, 0.0001) for n in sequence])

def mutate(sequence, number_pool):
    # Mutate by replacing one number
    new_seq = sequence[:]
    index_to_replace = random.randint(0, len(new_seq) - 1)
    new_number = random.choice([n for n in number_pool if n not in new_seq])
    new_seq[index_to_replace] = new_number
    return sorted(new_seq)

def smc_predict(draws, num_predictions=5, num_particles=100, iterations=5, sequence_length=4):
    freq_dist = compute_number_frequencies(draws)
    number_pool = list(freq_dist.keys())

    particles = initialize_particles(num_particles, number_pool, sequence_length)

    for _ in range(iterations):
        # Weight particles
        weights = [likelihood(p, freq_dist) for p in particles]

        # Normalize
        total_weight = sum(weights)
        if total_weight == 0:
            weights = [1/len(particles)] * len(particles)
        else:
            weights = [w / total_weight for w in weights]

        # Resample
        particles = random.choices(particles, weights=weights, k=num_particles)

        # Mutate
        particles = [mutate(p, number_pool) for p in particles]

    # Final predictions: return the most frequent or top-weighted unique sequences
    final_sequences = Counter(tuple(p) for p in particles)
    top_sequences = final_sequences.most_common(num_predictions)

    return [list(seq) for seq, _ in top_sequences]

def main():
    file_path = "merged_uk_49s_results.json"
    lottery_data = load_lottery_data(file_path)

    # User input
    time_filter = input("Enter draw time (lunchtime/teatime): ").strip().lower()
    num_predictions = int(input("How many 4-number predictions would you like to generate? "))

    dataset = get_filtered_draws(lottery_data, time_filter)

    print(f"\n🔮 {num_predictions} Predicted 4-number sequences using Sequential Monte Carlo:")
    predictions = smc_predict(dataset, num_predictions=num_predictions)
    for pred in predictions:
        print(pred)

if __name__ == "__main__":
    main()
