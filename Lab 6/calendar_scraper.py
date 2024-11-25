import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import csv
import random


mim_start = "1975-01-01"
today = date.today()
past_date = datetime.strptime(mim_start, "%Y-%m-%d").date()
days_difference = (today - past_date).days + 365 # Let's find all since the beginning of MIM until next year

url = ("https://mimuw.edu.pl/en/events/events/?init_date=" + mim_start + "&start_offset=0&end_offset=" +
       str(days_difference) + "&query_type=A")
response = requests.get(url)
data = response.json()

events = []
for event in data['events']:
    event_details = {}
    title = None
    link = None
    date = None
    for item in event['data']:
        if item['label'] == "Title":
            title = item['text']
            link = item.get('link')
        if item['label'] == "From":
            date = item['text']
    if title and date:
        events.append({
            "title": title,
            "link": f"https://mimuw.edu.pl{link}" if link else None,
            "date": date
        })

csv_filename = "events.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["title", "link", "date"])
    writer.writeheader()
    writer.writerows(events)

random_events = random.sample(events, 5)
print("Randomly Selected Events:")
for event in random_events:
    print(event)
