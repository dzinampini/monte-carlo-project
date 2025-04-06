# Genetic algorithms (GA) are a search heuristic inspired by natural selection. They work by evolving a population of possible solutions (in our case, lottery number combinations) over several generations. The goal is to converge to an optimal or near-optimal solution.

# Steps to Implement GMC:
# Initial Population: Create a population of possible lottery number combinations (e.g., random sequences).

# Fitness Function: Evaluate how "fit" each combination is based on historical data (i.e., how often a combination of numbers appears).

# Selection: Choose the best-performing combinations for reproduction.

# Crossover: Combine pairs of selected combinations to create new offspring (new predictions).

# Mutation: Introduce random changes to offspring to maintain diversity.

# Termination: Repeat the process for several generations, then select the best-performing combination.

import random
import json
from collections import Counter

def load_lottery_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def get_filtered_draws(data, draw_time):
    return [entry for entry in data if entry['time'].lower() == draw_time]

def generate_initial_population(draws, population_size=100):
    """Generate an initial population of random number combinations."""
    all_numbers = [num for entry in draws for num in entry['numbers']]
    population = []
    for _ in range(population_size):
        individual = sorted(random.sample(all_numbers, 4))  # Randomly sample 4 numbers
        population.append(individual)
    return population

def fitness_function(individual, draws):
    """Fitness function based on how frequently the individual (lottery numbers) appears in draws."""
    match_count = 0
    for entry in draws:
        if set(individual).issubset(entry['numbers']):  # Check if the combination is in the draw
            match_count += 1
    return match_count

def selection(population, draws, num_parents=50):
    """Select the best individuals based on fitness."""
    fitness_scores = [(individual, fitness_function(individual, draws)) for individual in population]
    fitness_scores.sort(key=lambda x: x[1], reverse=True)  # Sort by fitness score
    parents = [individual for individual, _ in fitness_scores[:num_parents]]
    return parents

def crossover(parents, offspring_size=50):
    """Crossover function to create offspring from selected parents."""
    offspring = []
    while len(offspring) < offspring_size:
        parent1, parent2 = random.sample(parents, 2)
        # Perform single-point crossover
        crossover_point = random.randint(1, 3)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        offspring.append(sorted(child))
    return offspring

def mutate(offspring, mutation_rate=0.1):
    """Mutation function to introduce randomness into the offspring."""
    for individual in offspring:
        if random.random() < mutation_rate:
            mutation_point = random.randint(0, 3)
            mutation_value = random.randint(1, 49)  # Mutate to a random valid number
            individual[mutation_point] = mutation_value
            individual.sort()
    return offspring

def genetic_monte_carlo_predict(draws, generations=100, population_size=100, num_predictions=5):
    """Run the Genetic Monte Carlo method to predict lottery numbers."""
    population = generate_initial_population(draws, population_size)
    
    for generation in range(generations):
        parents = selection(population, draws)
        offspring = crossover(parents)
        population = mutate(offspring)
    
    # After generations, select the top predictions
    fitness_scores = [(individual, fitness_function(individual, draws)) for individual in population]
    fitness_scores.sort(key=lambda x: x[1], reverse=True)
    top_predictions = [individual for individual, _ in fitness_scores[:num_predictions]]
    
    return top_predictions

def main():
    file_path = "merged_uk_49s_results.json"
    lottery_data = load_lottery_data(file_path)

    # User input
    time_filter = input("Enter draw time (lunchtime/teatime): ").strip().lower()
    num_predictions = int(input("How many 4-number predictions would you like to generate? "))

    dataset = get_filtered_draws(lottery_data, time_filter)
    # dataset = lottery_data

    print(f"\n🔄 {num_predictions} Predictions using Genetic Monte Carlo:")
    predictions = genetic_monte_carlo_predict(dataset, num_predictions=num_predictions)
    for pred in predictions:
        print(pred)

if __name__ == "__main__":
    main()
