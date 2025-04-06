# I have this lottery data and I wish to do some statistical analysis of this data detailing the following:
# [
#     {
#         "date": "2025-03-23",
#         "time": "lunchtime",
#         "numbers": [
#             16,
#             24,
#             32,
#             43,
#             44,
#             49,
#             27
#         ]
#     },
#     ...
# ]

# # number frequencies 
# 1. check each number's frequency from the begining of time and Rank the numbers according to this frequency. The numbers are 1-49  
# 2. check each number's frequency and give probability of recurrence of each number according to this frequency. 
# 3. get probability of occurence of each number on a particular day of the month 
# 4. get probability of occurence of each number on a particular day of the week 

import json
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta
from tabulate import tabulate

import requests
from bs4 import BeautifulSoup
import re

def load_lottery_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Process data into a DataFrame
def process_data(lottery_data):
    records = []
    for entry in lottery_data:
        date_obj = datetime.strptime(entry["date"], "%Y-%m-%d")
        for num in entry["numbers"]:
            records.append({
                "date": entry["date"],
                "time": entry["time"],
                "dom": date_obj.day,
                "dow": date_obj.strftime("%A"),
                "number": num
            })
    return pd.DataFrame(records)

# Compute number frequency and ranking
def number_frequency(df):
    freq = Counter(df["number"])
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    total_draws = len(df) / 7  # Since each draw has 7 numbers
    probability = {num: round(count / total_draws, 3) for num, count in freq.items()}
    return sorted_freq, probability

# Probability per day of the month
def probability_per_day_of_month(df):
    grouped = df.groupby(["dom", "number"]).size().unstack(fill_value=0)
    total_per_day = df.groupby("dom").size()
    prob_df = (grouped.div(total_per_day, axis=0)).fillna(0).round(3)
    return prob_df.T

# Probability per day of the week
def probability_per_day_of_week(df):
    grouped = df.groupby(["dow", "number"]).size().unstack(fill_value=0)
    total_per_day = df.groupby("dow").size()
    prob_df = (grouped.div(total_per_day, axis=0)).fillna(0).round(3)
    return prob_df.T

def yester_check(generated_number_frequencies, play_numbers):
    result = []
    
    # Iterate over each play number
    for play_number in play_numbers:
        frequency = 0
        description = []
        
        # print(generated_number_frequencies)
        for record in generated_number_frequencies:
            # print(record['probability'])
            if record['number'] == play_number:
                frequency += 1
                description.append(record['coming_from'])
        
        # Append the result for the current play_number
        result.append({
            "number": play_number,
            "frequency": frequency,
            "description": description
        })
    
    return result

def top_numbers(number_frequencies):
    numbers = [entry["number"] for entry in number_frequencies]
    number_counts = Counter(numbers)
    top_3_numbers = number_counts.most_common(7)
    return top_3_numbers

def top_3_numbers_with_play_number(lottery_data, play_number):
    co_occurring_numbers = []

    # Step 1: Loop through dataset to find play_number occurrences
    for draw in lottery_data:
        numbers = draw["numbers"]
        if play_number in numbers:
            # Step 2: Add all other numbers in the same draw
            co_occurring_numbers.extend([num for num in numbers if num != play_number])

    # Step 3: Count occurrences of co-occurring numbers
    number_counts = Counter(co_occurring_numbers)

    # Step 4: Get the top 3 numbers played alongside play_number
    top_3 = number_counts.most_common(3)

    return top_3


def scrap_link(url, last_day, time):
    response = requests.get(url)
    results = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr")
        
        
        for row in rows:
            columns = row.find_all("td")

            if len(columns) > 1:
                date_str = columns[0].text.strip()
                try:
                    date_str = " ".join(date_str.split(" ")[1:])  # Removes "Thursday"
                    date_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)  # Converts "26th" → "26"
                    
                    date_obj = datetime.strptime(date_str, "%d %B %Y")
                    formatted_date = date_obj.strftime("%Y-%m-%d")  # Convert to YYYY-MM-DD
                    
                except ValueError:
                    print('Invalid date', columns[0].text)
                    continue  # Skip rows with invalid dates
                
                try:
                    numbers = [int(num.text.strip()) for num in columns[1].find_all("li")]
                except ValueError:
                    print('Invalid value skipped')
                    continue
                # print('about to compare')
                if (datetime.strptime(formatted_date, "%Y-%m-%d").date() >= last_day):
                    # print('comp done')
                    draw_data = {
                        "date": formatted_date,
                        "time": time,
                        "numbers": numbers
                    }
                    results.append(draw_data)
    return results



def update_dataset(data):
    first_record = data[0]
    play_time = 0

    day_today = datetime.today().date()
    last_recorded_day = datetime.strptime(first_record['date'], "%Y-%m-%d").date()

    if (first_record['time'] == 'lunchtime'):
        play_time = 1
    elif (first_record['time'] == 'teatime'):
        play_time = 0 
        last_recorded_day = last_recorded_day + timedelta(days=1)

    all_results = []

    url = "https://za.lottonumbers.com/"
    url = url+"uk-49s-lunchtime/results/2025"
    get_lunchtime_data = scrap_link(url, last_recorded_day, 'lunchtime')
    all_results.extend(
        get_lunchtime_data,
    )


    url = "https://za.lottonumbers.com/"
    url = url+"uk-49s-teatime/results/2025"
    get_teatime_data = scrap_link(url, last_recorded_day, 'teatime')
    all_results.extend(
        get_teatime_data,
    )

    # extend original json data 
    all_results.extend(
        data,
    )
    
    all_results.sort(
        key=lambda x: (datetime.strptime(x["date"], "%Y-%m-%d"), 1 if x["time"] == "teatime" else 0), 
        reverse=True  # Sort by date descending, then time descending
    )

    with open("merged_uk_49s_results.json", "w") as output_file:
        json.dump(all_results, output_file, indent=4)




if __name__ == "__main__":
    today_dom = 24
    today_dow = 'Monday'
    # Using number frequencies 
    file_path = "merged_uk_49s_results.json"
    lottery_data = load_lottery_data(file_path)

    update_dataset(lottery_data)
    

    # yester play results 
    play_lunchtime_numbers = [1, 2, 4, 7, 8, 9, 12]
    play_teatime_numbers = [1,2,15,31,42,46,48]
    
    full_dataset_df = process_data(lottery_data)

    full_lunchtime_df = full_dataset_df[full_dataset_df["time"] == "lunchtime"]
    full_teatime_df = full_dataset_df[full_dataset_df["time"] == "teatime"]

    full_dataset_df["date"] = pd.to_datetime(full_dataset_df["date"])
    full_lunchtime_df["date"] = pd.to_datetime(full_lunchtime_df["date"])
    full_teatime_df["date"] = pd.to_datetime(full_teatime_df["date"])

    cutoff_date = datetime.today() - timedelta(days=49)

    last49_dataset_df = full_dataset_df[full_dataset_df["date"] >= cutoff_date]
    last49_lunchtime_df = full_lunchtime_df[full_lunchtime_df["date"] >= cutoff_date]
    last49_teatime_df = full_teatime_df[full_teatime_df["date"] >= cutoff_date]
   
    
    print("\n############################################Number Frequency Ranking########################################")
    sorted_freq, probability = number_frequency(full_dataset_df)
    # for rank, (num, count) in enumerate(sorted_freq, 1):
    #     print(f"{rank}. Number {num} - {count} times (Probability: {probability[num]})")
    
    top_6_numbers = sorted_freq[:6] 
    all_top_sample = [{"number": num, "probability": probability[num], "coming_from": "all_top_sample"} for num, count in top_6_numbers]

    bottom_6_numbers = sorted_freq[-6:]
    all_bottom_sample = [{"number": num, "probability": probability[num], "coming_from": "all_bottom_sample"} for num, count in bottom_6_numbers]

    # print('all top sample', all_top_sample)
    # print('all bottom sample', all_bottom_sample)

    sorted_freq, probability = number_frequency(full_lunchtime_df)
    top_6_numbers = sorted_freq[:6] 
    all_top_lunchtime_sample = [{"number": num, "probability": probability[num], "coming_from": "all_top_lunchtime_sample"} for num, count in top_6_numbers]

    bottom_6_numbers = sorted_freq[-6:]
    all_bottom_lunchtime_sample = [{"number": num, "probability": probability[num], "coming_from": "all_bottom_lunchtime_sample"} for num, count in bottom_6_numbers]

    # print('all top lunchtime sample', all_top_lunchtime_sample)
    # print('all bottom lunchtime sample', all_bottom_lunchtime_sample) 

    sorted_freq, probability = number_frequency(full_teatime_df)
    top_6_numbers = sorted_freq[:6] 
    all_top_teatime_sample = [{"number": num, "probability": probability[num], "coming_from": "all_top_teatime_sample"} for num, count in top_6_numbers]

    bottom_6_numbers = sorted_freq[-6:]
    all_bottom_teatime_sample = [{"number": num, "probability": probability[num], "coming_from": "all_bottom_teatime_sample"} for num, count in bottom_6_numbers]

    # print('all top teatime sample', all_top_teatime_sample)
    # print('all bottom teatime sample', all_bottom_teatime_sample)



    sorted_freq, probability = number_frequency(last49_dataset_df)
    
    top_6_numbers = sorted_freq[:6] 
    last49_top_sample = [{"number": num, "probability": probability[num], "coming_from": "last49_top_sample"} for num, count in top_6_numbers]

    bottom_6_numbers = sorted_freq[-6:]
    last49_bottom_sample = [{"number": num, "probability": probability[num], "coming_from": "last49_bottom_sample"} for num, count in bottom_6_numbers]

    sorted_freq, probability = number_frequency(last49_lunchtime_df)
    top_6_numbers = sorted_freq[:6] 
    last49_top_lunchtime_sample = [{"number": num, "probability": probability[num], "coming_from": "last49_top_lunchtime_sample"} for num, count in top_6_numbers]

    bottom_6_numbers = sorted_freq[-6:]
    last49_bottom_lunchtime_sample = [{"number": num, "probability": probability[num], "coming_from": "last49_bottom_lunchtime_sample"} for num, count in bottom_6_numbers]

    sorted_freq, probability = number_frequency(last49_teatime_df)
    top_6_numbers = sorted_freq[:6] 
    last49_top_teatime_sample = [{"number": num, "probability": probability[num], "coming_from": "last49_top_teatime_sample"} for num, count in top_6_numbers]

    bottom_6_numbers = sorted_freq[-6:]
    last49_bottom_teatime_sample = [{"number": num, "probability": probability[num], "coming_from": "last49_bottom_teatime_sample"} for num, count in bottom_6_numbers]

    
    
    print("\n########################################################Probability of Occurrence per Day of the Month#########################")
    prob_dom = probability_per_day_of_month(full_dataset_df)
    # print(prob_dom.columns)

    today_prob = prob_dom[[today_dom]]
    top_6_numbers = today_prob.sort_values(by=today_dom, ascending=False).head(6)
    # print(top_6_numbers)
    
    # date_top_sample = [{"number": ?value1, "probability": ?value1, "coming_from": "date_top_sample"} for num, count in top_6_numbers]
    all_date_top_sample = [
        {"number": num, "probability": top_6_numbers[today_dom].loc[num], "coming_from": "all_date_top_sample"}
        for num in top_6_numbers.index
    ]
    # print(date_top_sample)

    # Sort the probabilities in ascending order for bottom probabilities
    bottom_6_numbers = today_prob.sort_values(by=today_dom, ascending=True).head(6)
    all_date_bottom_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dom].loc[num], "coming_from": "all_date_bottom_sample"}
        for num in bottom_6_numbers.index
    ] 



    prob_dom = probability_per_day_of_month(full_lunchtime_df)
    # print(prob_dom.columns)

    today_prob = prob_dom[[today_dom]]
    top_6_numbers = today_prob.sort_values(by=today_dom, ascending=False).head(6)
    # print(top_6_numbers)
    
    # date_top_sample = [{"number": ?value1, "probability": ?value1, "coming_from": "date_top_sample"} for num, count in top_6_numbers]
    all_date_top_lunchtime_sample = [
        {"number": num, "probability": top_6_numbers[today_dom].loc[num], "coming_from": "all_date_top_lunchtime_sample"}
        for num in top_6_numbers.index
    ]
    # print(date_top_sample)

    # Sort the probabilities in ascending order for bottom probabilities
    bottom_6_numbers = today_prob.sort_values(by=today_dom, ascending=True).head(6)
    all_date_bottom_lunchtime_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dom].loc[num], "coming_from": "all_date_bottom_lunchtime_sample"}
        for num in bottom_6_numbers.index
    ] 



    prob_dom = probability_per_day_of_month(full_teatime_df)
    # print(prob_dom.columns)

    today_prob = prob_dom[[today_dom]]
    top_6_numbers = today_prob.sort_values(by=today_dom, ascending=False).head(6)
    # print(top_6_numbers)
    
    # date_top_sample = [{"number": ?value1, "probability": ?value1, "coming_from": "date_top_sample"} for num, count in top_6_numbers]
    all_date_top_teatime_sample = [
        {"number": num, "probability": top_6_numbers[today_dom].loc[num], "coming_from": "all_date_top_teatime_sample"}
        for num in top_6_numbers.index
    ]
    # print(date_top_sample)

    # Sort the probabilities in ascending order for bottom probabilities
    bottom_6_numbers = today_prob.sort_values(by=today_dom, ascending=True).head(6)
    all_date_bottom_teatime_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dom].loc[num], "coming_from": "all_date_bottom_teatime_sample"}
        for num in bottom_6_numbers.index
    ] 





    prob_dom = probability_per_day_of_month(last49_dataset_df)
    # print(prob_dom.columns)

    today_prob = prob_dom[[today_dom]]
    top_6_numbers = today_prob.sort_values(by=today_dom, ascending=False).head(6)
    # print(top_6_numbers)
    
    # date_top_sample = [{"number": ?value1, "probability": ?value1, "coming_from": "date_top_sample"} for num, count in top_6_numbers]
    last49_date_top_sample = [
        {"number": num, "probability": top_6_numbers[today_dom].loc[num], "coming_from": "last49_date_top_sample"}
        for num in top_6_numbers.index
    ]
    # print(date_top_sample)

    # Sort the probabilities in ascending order for bottom probabilities
    bottom_6_numbers = today_prob.sort_values(by=today_dom, ascending=True).head(6)
    last49_date_bottom_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dom].loc[num], "coming_from": "last49_date_bottom_sample"}
        for num in bottom_6_numbers.index
    ]


    prob_dom = probability_per_day_of_month(last49_lunchtime_df)
    # print(prob_dom.columns)

    today_prob = prob_dom[[today_dom]]
    top_6_numbers = today_prob.sort_values(by=today_dom, ascending=False).head(6)
    # print(top_6_numbers)
    
    # date_top_sample = [{"number": ?value1, "probability": ?value1, "coming_from": "date_top_sample"} for num, count in top_6_numbers]
    last49_date_top_lunchtime_sample = [
        {"number": num, "probability": top_6_numbers[today_dom].loc[num], "coming_from": "last49_date_top_lunchtime_sample"}
        for num in top_6_numbers.index
    ]
    # print(date_top_sample)

    # Sort the probabilities in ascending order for bottom probabilities
    bottom_6_numbers = today_prob.sort_values(by=today_dom, ascending=True).head(6)
    last49_date_bottom_lunchtime_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dom].loc[num], "coming_from": "last49_date_bottom_lunchtime_sample"}
        for num in bottom_6_numbers.index
    ]



    prob_dom = probability_per_day_of_month(last49_teatime_df)
    # print(prob_dom.columns)

    today_prob = prob_dom[[today_dom]]
    top_6_numbers = today_prob.sort_values(by=today_dom, ascending=False).head(6)
    # print(top_6_numbers)
    
    # date_top_sample = [{"number": ?value1, "probability": ?value1, "coming_from": "date_top_sample"} for num, count in top_6_numbers]
    last49_date_top_teatime_sample = [
        {"number": num, "probability": top_6_numbers[today_dom].loc[num], "coming_from": "last49_date_top_teatime_sample"}
        for num in top_6_numbers.index
    ]
    # print(date_top_sample)

    # Sort the probabilities in ascending order for bottom probabilities
    bottom_6_numbers = today_prob.sort_values(by=today_dom, ascending=True).head(6)
    last49_date_bottom_teatime_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dom].loc[num], "coming_from": "last49_date_bottom_teatime_sample"}
        for num in bottom_6_numbers.index
    ]

    
    
    print("\n###################################################Probability of Occurrence per Day of the Week#######################")
    prob_dow = probability_per_day_of_week(full_dataset_df)
    # print(prob_dow)

    today_prob = prob_dow[[today_dow]]
    # print(today_prob)
    top_6_numbers = today_prob.sort_values(by=today_dow, ascending=False).head(6)
    all_day_top_sample = [
        {"number": num, "probability": top_6_numbers[today_dow].loc[num], "coming_from": "all_day_top_sample"}
        for num in top_6_numbers.index
    ]

    bottom_6_numbers = today_prob.sort_values(by=today_dow, ascending=True).head(6)
    all_day_bottom_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dow].loc[num], "coming_from": "all_day_bottom_sample"}
        for num in bottom_6_numbers.index
    ] 



    prob_dow = probability_per_day_of_week(full_lunchtime_df)
    # print(prob_dow)

    today_prob = prob_dow[[today_dow]]
    # print(today_prob)
    top_6_numbers = today_prob.sort_values(by=today_dow, ascending=False).head(6)
    all_day_top_lunchtime_sample = [
        {"number": num, "probability": top_6_numbers[today_dow].loc[num], "coming_from": "all_day_top_lunchtime_sample"}
        for num in top_6_numbers.index
    ]

    bottom_6_numbers = today_prob.sort_values(by=today_dow, ascending=True).head(6)
    all_day_bottom_lunchtime_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dow].loc[num], "coming_from": "all_day_bottom_lunchtime_sample"}
        for num in bottom_6_numbers.index
    ]


    prob_dow = probability_per_day_of_week(full_teatime_df)
    # print(prob_dow)

    today_prob = prob_dow[[today_dow]]
    # print(today_prob)
    top_6_numbers = today_prob.sort_values(by=today_dow, ascending=False).head(6)
    all_day_top_teatime_sample = [
        {"number": num, "probability": top_6_numbers[today_dow].loc[num], "coming_from": "all_day_top_teatime_sample"}
        for num in top_6_numbers.index
    ]

    bottom_6_numbers = today_prob.sort_values(by=today_dow, ascending=True).head(6)
    all_day_bottom_teatime_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dow].loc[num], "coming_from": "all_day_bottom_teatime_sample"}
        for num in bottom_6_numbers.index
    ] 





    prob_dow = probability_per_day_of_week(last49_dataset_df)
    # print(prob_dow)

    today_prob = prob_dow[[today_dow]]
    # print(today_prob)
    top_6_numbers = today_prob.sort_values(by=today_dow, ascending=False).head(6)
    last49_day_top_sample = [
        {"number": num, "probability": top_6_numbers[today_dow].loc[num], "coming_from": "last49_day_top_sample"}
        for num in top_6_numbers.index
    ]

    bottom_6_numbers = today_prob.sort_values(by=today_dow, ascending=True).head(6)
    last49_day_bottom_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dow].loc[num], "coming_from": "last49_day_bottom_sample"}
        for num in bottom_6_numbers.index
    ]

    prob_dow = probability_per_day_of_week(last49_lunchtime_df)
    # print(prob_dow)

    today_prob = prob_dow[[today_dow]]
    # print(today_prob)
    top_6_numbers = today_prob.sort_values(by=today_dow, ascending=False).head(6)
    last49_day_top_lunchtime_sample = [
        {"number": num, "probability": top_6_numbers[today_dow].loc[num], "coming_from": "last49_day_top_lunchtime_sample"}
        for num in top_6_numbers.index
    ]

    bottom_6_numbers = today_prob.sort_values(by=today_dow, ascending=True).head(6)
    last49_day_bottom_lunchtime_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dow].loc[num], "coming_from": "last49_day_bottom_lunchtime_sample"}
        for num in bottom_6_numbers.index
    ]

    prob_dow = probability_per_day_of_week(last49_teatime_df)
    # print(prob_dow)

    today_prob = prob_dow[[today_dow]]
    # print(today_prob)
    top_6_numbers = today_prob.sort_values(by=today_dow, ascending=False).head(6)
    last49_day_top_teatime_sample = [
        {"number": num, "probability": top_6_numbers[today_dow].loc[num], "coming_from": "last49_day_top_teatime_sample"}
        for num in top_6_numbers.index
    ]

    bottom_6_numbers = today_prob.sort_values(by=today_dow, ascending=True).head(6)
    last49_day_bottom_teatime_sample = [
        {"number": num, "probability": bottom_6_numbers[today_dow].loc[num], "coming_from": "last49_day_bottom_teatime_sample"}
        for num in bottom_6_numbers.index
    ] 

    merged_all_number_frequencies = (
        all_top_sample +
        all_bottom_sample +
        all_top_lunchtime_sample +
        all_bottom_lunchtime_sample +
        all_top_teatime_sample +
        all_bottom_teatime_sample + 

        all_date_top_sample + 
        all_date_bottom_sample +
        all_date_top_lunchtime_sample + 
        all_date_bottom_lunchtime_sample +
        all_date_top_teatime_sample + 
        all_date_bottom_teatime_sample +
        
        all_day_top_sample +
        all_day_bottom_sample +
        all_day_top_lunchtime_sample +
        all_day_bottom_lunchtime_sample +
        all_day_top_teatime_sample +
        all_day_bottom_teatime_sample +

        last49_top_sample +
        last49_bottom_sample +
        last49_top_lunchtime_sample +
        last49_bottom_lunchtime_sample +
        last49_top_teatime_sample +
        last49_bottom_teatime_sample + 

        last49_date_top_sample + 
        last49_date_bottom_sample +
        last49_date_top_lunchtime_sample + 
        last49_date_bottom_lunchtime_sample +
        last49_date_top_teatime_sample + 
        last49_date_bottom_teatime_sample +
        
        last49_day_top_sample +
        last49_day_bottom_sample +
        last49_day_top_lunchtime_sample +
        last49_day_bottom_lunchtime_sample +
        last49_day_top_teatime_sample +
        last49_day_bottom_teatime_sample 
    )
    # print(tabulate(merged_all_number_frequencies, headers="keys", tablefmt="grid"))


    merged_lunchtime_number_frequencies = (
        all_top_sample +
        all_bottom_sample +
        all_top_lunchtime_sample +
        all_bottom_lunchtime_sample +
        # all_top_teatime_sample +
        # all_bottom_teatime_sample + 

        all_date_top_sample + 
        all_date_bottom_sample +
        all_date_top_lunchtime_sample + 
        all_date_bottom_lunchtime_sample +
        # all_date_top_teatime_sample + 
        # all_date_bottom_teatime_sample +
        
        all_day_top_sample +
        all_day_bottom_sample +
        all_day_top_lunchtime_sample +
        all_day_bottom_lunchtime_sample +
        # all_day_top_teatime_sample +
        # all_day_bottom_teatime_sample +

        last49_top_sample +
        last49_bottom_sample +
        last49_top_lunchtime_sample +
        last49_bottom_lunchtime_sample +
        # last49_top_teatime_sample +
        # last49_bottom_teatime_sample + 

        last49_date_top_sample + 
        last49_date_bottom_sample +
        last49_date_top_lunchtime_sample + 
        last49_date_bottom_lunchtime_sample +
        # last49_date_top_teatime_sample + 
        # last49_date_bottom_teatime_sample +
        
        last49_day_top_sample +
        last49_day_bottom_sample +
        last49_day_top_lunchtime_sample +
        last49_day_bottom_lunchtime_sample 
        # last49_day_top_teatime_sample +
        # last49_day_bottom_teatime_sample 
    )


    merged_teatime_number_frequencies = (
        all_top_sample +
        all_bottom_sample +
        # all_top_lunchtime_sample +
        # all_bottom_lunchtime_sample +
        all_top_teatime_sample +
        all_bottom_teatime_sample + 

        all_date_top_sample + 
        all_date_bottom_sample +
        # all_date_top_lunchtime_sample + 
        # all_date_bottom_lunchtime_sample +
        all_date_top_teatime_sample + 
        all_date_bottom_teatime_sample +
        
        all_day_top_sample +
        all_day_bottom_sample +
        # all_day_top_lunchtime_sample +
        # all_day_bottom_lunchtime_sample +
        all_day_top_teatime_sample +
        all_day_bottom_teatime_sample +

        last49_top_sample +
        last49_bottom_sample +
        # last49_top_lunchtime_sample +
        # last49_bottom_lunchtime_sample +
        last49_top_teatime_sample +
        last49_bottom_teatime_sample + 

        last49_date_top_sample + 
        last49_date_bottom_sample +
        # last49_date_top_lunchtime_sample + 
        # last49_date_bottom_lunchtime_sample +
        last49_date_top_teatime_sample + 
        last49_date_bottom_teatime_sample +
        
        last49_day_top_sample +
        last49_day_bottom_sample +
        # last49_day_top_lunchtime_sample +
        # last49_day_bottom_lunchtime_sample +
        last49_day_top_teatime_sample +
        last49_day_bottom_teatime_sample 
    )

    # print("\n###################################################Measure results impact#######################")
    # lunchtime_impact = yester_check(merged_all_number_frequencies, play_lunchtime_numbers)
    # print(tabulate(lunchtime_impact, headers="keys", tablefmt="grid"))

    # teatime_impact = yester_check(merged_all_number_frequencies, play_teatime_numbers)
    # print(tabulate(teatime_impact, headers="keys", tablefmt="grid"))


    # Using number combinations.
    # goal is to get a definite number and find combinations we can put to it  
    lunchtime_play_suggestion = top_numbers(merged_lunchtime_number_frequencies)
    teatime_play_suggestion = top_numbers(merged_teatime_number_frequencies)

    print('lunchtime')
    for record in lunchtime_play_suggestion:
        play_number = record[0]
        top_3 = top_3_numbers_with_play_number(lottery_data, play_number)
        for one in top_3:
            print(play_number, one[0])

    print('\n\nteatime')
    for record in teatime_play_suggestion:
        play_number = record[0]
        top_3 = top_3_numbers_with_play_number(lottery_data, play_number)
        for one in top_3:
            print(play_number, one[0])

     

