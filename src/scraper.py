from bs4 import BeautifulSoup
import requests

#page_link = "https://riceowls.com/sports/mens-basketball/stats/2021-22/north-texas/boxscore/25321"
page_link = "https://riceowls.com/sports/mens-basketball/stats/2021-22/uab/boxscore/25323"
page_response = requests.get(page_link)
page_content = BeautifulSoup(page_response.content, "html.parser")

final_data = []
next_entry = []

initial_data = []
next_initial = []

for i in range(3900):
    print(str(i) + ": " + str(page_content.find_all("td")[i].text))

for i in range(930, 3786):
    if i % 8 == 2:
        initial_data.append(next_initial)
        next_initial = []
    words = page_content.find_all("td")[i].text
    next_initial.append(words)

initial_data = initial_data[1:]


score = (0,0)

print(initial_data)
