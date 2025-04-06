import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import re

first_year = 1996
current_year = 2025
while (first_year <= current_year):
    play_time = 0
    url = "https://za.lottonumbers.com/"
    time = ""
    while(play_time <= 1):
        url = "https://za.lottonumbers.com/"
        if (play_time == 0):
            url = url+"uk-49s-lunchtime/results/"
            time = "lunchtime"
        elif(play_time == 1):
            url = url+"uk-49s-teatime/results/"
            time = "teatime"
        
        print("Working on " + str(first_year) + " part " + str(play_time))

        url = url + str(first_year)
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr")

            results = []

            for row in rows:
                columns = row.find_all("td")

                if len(columns) > 1:
                    date_str = columns[0].text.strip()
                    try:
                        date_str = " ".join(date_str.split(" ")[1:])  # Removes "Thursday"
                        # Remove ordinal suffix (st, nd, rd, th) using regex
                        date_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)  # Converts "26th" → "26"

                        # Parse the cleaned date
                        date_obj = datetime.strptime(date_str, "%d %B %Y")
                        formatted_date = date_obj.strftime("%Y-%m-%d")  # Convert to YYYY-MM-DD
                    except ValueError:
                        print('Invalid date', columns[0].text)
                        continue  # Skip rows with invalid dates

                    # 3. Get list item values (lottery numbers)
                    try:
                        numbers = [int(num.text.strip()) for num in columns[1].find_all("li")]
                    except ValueError:
                        print('Invalid value skipped')
                        continue

                    # 4. Store data in JSON format
                    draw_data = {
                        "date": formatted_date,
                        "time": time,
                        "numbers": numbers
                    }
                    results.append(draw_data)

            filename = url.removeprefix("https://za.lottonumbers.com/")
            filename = filename.replace("/", "-")
            filename = filename + ".json"
            with open(filename, "w", encoding="utf-8") as json_file:
                json.dump(results, json_file, indent=4)

            print(f"Data successfully saved to {filename}")

        else:
            print("Failed to retrieve " + url + " results")

        play_time = play_time + 1 

    first_year = first_year + 1
