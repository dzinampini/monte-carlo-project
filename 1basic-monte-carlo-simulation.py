import random
import json
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

def load_lottery_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


file_path = "merged_uk_49s_results.json"
lottery_data = load_lottery_data(file_path)


lunchtime_draws = [entry for entry in lottery_data if entry['time'] == 'lunchtime']
teatime_draws = [entry for entry in lottery_data if entry['time'] == 'teatime']

time_filter = input("Enter draw time (lunchtime/teatime): ").strip().lower()
num_predictions = int(input("How many 4-number predictions would you like to generate? "))

dataset = lunchtime_draws
if (time_filter == 'teatime'):
    dataset = teatime_draws

# Step 1: Aggregate all numbers
all_numbers = []
for draw in dataset:
    all_numbers.extend(draw['numbers'])

# Step 2: Count frequency of each number
freq = Counter(all_numbers)

# Step 3: Normalize to probability distribution
total_counts = sum(freq.values())
prob_dist = {num: count / total_counts for num, count in freq.items()}

# Step 4: Monte Carlo sampling of specified unique numbers
def sample_lottery_numbers(prob_dist, k=num_predictions):
    numbers = list(prob_dist.keys())
    weights = list(prob_dist.values())
    return random.choices(numbers, weights=weights, k=k)

predicted_numbers = sample_lottery_numbers(prob_dist)
print("Play numbers:", predicted_numbers)
