def scrap_link(url):
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
                
                draw_data = {
                    "date": formatted_date,
                    "time": time,
                    "numbers": numbers
                }
                results.append(draw_data)