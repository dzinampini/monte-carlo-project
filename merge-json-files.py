import json
from datetime import datetime

first_year = 1996
current_year = 2025
all_results = []

while first_year <= current_year:
    play_time = 0
    while play_time <= 1:
        file_path = "uk-49s-"
        
        if play_time == 0:
            file_path += "lunchtime"
        else:
            file_path += "teatime"
        
        file_path += f"-results-{first_year}.json"
        
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                all_results.extend(
                    data,
                )
        except FileNotFoundError:
            print(f"Warning: {file_path} not found.")
        except json.JSONDecodeError:
            print(f"Error: {file_path} contains invalid JSON.")
        
        play_time += 1
    
    first_year += 1

# sort results 
all_results.sort(
    key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), 
    reverse=True
)

# Save merged results into one JSON file
with open("merged_uk_49s_results.json", "w") as output_file:
    json.dump(all_results, output_file, indent=4)

print("Merged JSON file created successfully.")
