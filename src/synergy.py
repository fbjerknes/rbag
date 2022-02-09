
# Imports allowing the use of Selenium and Geckodriver.
from lxml import html
from selenium import webdriver
# Allows us to send keys through the Webdriver.
from selenium.webdriver.common.keys import Keys
# Allows us to wait for certain elements to load in. Gives us much more control over the Webdriver.
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Allows us to write a function that confirms the existence of an element (EBS issue)
from selenium.common.exceptions import NoSuchElementException
# Imported to use simple sleep function. (used rarely)
import time
# Import pandas allowing us to export Lists of Lists to excel files.
import pandas as pd


def teamData(team):
    ''' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Function aggregating EBS stats from every game of every team into each team's respective List of Lists of Lists.
    team - team whose data is currently being collected.
    data1 - list of list of lists storing all of the first tables of every game for this team
    data2 - same as above, but stores the second table of each game
    opp1 and opp2 - storage for the opponent's tables for each game
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - '''


    # create new driver
    driver = webdriver.Chrome(executable_path='/Users/fbjerknes/PycharmProjects/dosastuff/src/chromedriver.exe')
    driver.get("https://www.synergysportstech.com/synergy/")
    assert "Synergy" in driver.title

    # *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***
    # NOTE: USER: Insert Sports Synergy Tech Credentials below

    user = driver.find_element(By.NAME, "txtUserName")
    pword = driver.find_element(By.NAME, "txtPassword")

    # Clear previous inputs
    user.clear()
    pword.clear()

    # Send the User's SST Email and Pass to the text field elements
    user.send_keys("fmb1@rice.edu")  # Insert Email inside of quotes
    pword.send_keys("R!ceOwls21")  # Insert Password inside of quotes

    pword.send_keys(Keys.RETURN)  # Presses "Enter" Key, submitting the credentials to SST


    teamButton = driver.find_element(By.LINK_TEXT, "Team")
    teamButton.click()

    teamName = driver.find_element(By.NAME, "ctl00$MainContent$lstTeam")
    teamName.send_keys(team)

    time.sleep(5)

    offData = driver.find_element(By.XPATH, '//td[@id="mainBackgroundColumn"]').text

    defButton = driver.find_element(By.LINK_TEXT, "Defensive")
    defButton.click()

    time.sleep(5)

    defData = driver.find_element(By.XPATH, '//td[@id="mainBackgroundColumn"]').text

    cbButton = driver.find_element(By.LINK_TEXT, "Cumulative Box")
    cbButton.click()

    time.sleep(5)

    cbData = driver.find_element(By.XPATH, '//td[@id="mainBackgroundColumn"]').text

    driver.quit()  # Close driver once we get our data.

    return [offData, defData, cbData]


def process_data(data):

    lines = []
    last = 0

    for i in range(len(data)):
        if data[i] == '\n':
            lines.append(data[last:i])
            last = i+1

    lines = lines[6:]
    lines.append('')
    lines.append('')

    sections = {}

    last = 0

    for i in range(len(lines)):
        if (lines[i] == '' and lines[i-1] == ''):
            temp = lines[last+16:i-1]
            sections[lines[last]] = temp
            last = i+1

    table = {}

    for k, v in sections.items():
        t1 = {}
        for i in v:
            temp = 0
            t2 = []
            name = ''
            for j in range(len(i)):
                if i[j] == ' ':
                    if not (len(t2) == 5 and (ord(i[j+1]) < 47 or ord(i[j+1]) > 58)):
                        if name != '':
                            t2.append(i[temp:j])
                        elif ord(i[j+1]) > 47 and ord(i[j+1]) < 58:
                            name = i[:j]
                    temp = j+1
            t2.append(i[temp:])
            if name != '':
                while name[0] == ' ':
                    name = name[1:]
                t1[name] = t2
        table[k] = t1

    return table


def process_box(data):
    lines = []
    last = 0
    for i in range(len(data)):
        if data[i] == '\n':
            lines.append(data[last:i])
            last = i+1
    lines.append(data[last:])

    vals = []
    for i in lines:
        if "Team Totals" in i:
            prev = 0
            count = 0
            for j in range(len(i)):
                if i[j] == ' ':
                    count += 1
                    if count > 2 and i[prev:j] != "Team" and i[prev:j] != "Totals":
                        vals.append(i[prev:j])
                    prev = j+1
            vals.append(i[prev:])

    return vals



def google(tables, rice, sheet_name):
    print(tables)
    print(rice)
    print(sheet_name)


def main():
    team = "Purdue Boilermakers"
    sheet_name = ""

    data = teamData(team)
    tables = []
    for i in range(2):
        tables.append(process_data(data[i]))
    tables.append(process_box(data[2]))

    rice = teamData("Rice Owls")
    rtables = []
    for i in range(2):
        rtables.append(process_data(rice[i]))
    rtables.append(process_box(rice[2]))

    google(tables, rtables, sheet_name)


if __name__ == "__main__":
    main()