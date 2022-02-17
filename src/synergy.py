
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
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
file_name = 'client_key.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
client = gspread.authorize(creds)


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


def google(tables, rice, sheet_name, team_name):
    print(tables)
    print(rice)
    print(sheet_name)

    sheet = client.open('RBAG Scouting Reports 2021-22').worksheet(sheet_name)

    # 4 factors
    sheet.update_cell(12, 7, tables[0]['Overall Offense'][team_name][10])
    sheet.update_cell(12, 8, tables[0]['Overall Offense'][team_name][4][:-1])
    sheet.update_cell(13, 7, tables[0]['Overall Offense'][team_name][11])
    sheet.update_cell(14, 7, str(round((float(tables[2][12]) / float(tables[2][11])) * 100, 2)) + '%')
    sheet.update_cell(15, 7, tables[0]['Overall Offense'][team_name][12])

    sheet.update_cell(16, 7, tables[0]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][0])
    sheet.update_cell(17, 7, tables[0]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][9])
    sheet.update_cell(16, 8, tables[0]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][4][:-1])

    mid_rate = (float(tables[0]['Jump Shot Range - half court']["Short (<17')"][0][:-1]) +
               float(tables[0]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][0][:-1])) / 100
    sheet.update_cell(18, 7, str(round(float(tables[0]['Shot Attempt - Half Court']['Jump Shots'][0][:-1]) * mid_rate, 2)) + '%')
    mid_makes = float(tables[0]['Jump Shot Range - half court']["Short (<17')"][7]) + \
               float(tables[0]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][7])
    mid_total = float(tables[0]['Jump Shot Range - half court']["Short (<17')"][8]) + \
               float(tables[0]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][8])
    sheet.update_cell(19, 7, str(round(100 * mid_makes / mid_total, 2)) + '%')
    mid_pct = (int(tables[0]['Jump Shot Range - half court']["Short (<17')"][4][:-1]) +
               int(tables[0]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][4][:-1])) // 2
    sheet.update_cell(18, 8, mid_pct)

    three_rate = float(tables[0]['Shot Attempt - Half Court']['Jump Shots'][0][:-1]) * \
               float(tables[0]['Jump Shot Range - half court']["Long (3 point jump shots)"][0][:-1]) / 100
    sheet.update_cell(20, 7, str(round(three_rate, 2)) + '%')
    sheet.update_cell(21, 7, tables[0]['Jump Shot Range - half court']["Long (3 point jump shots)"][9])
    sheet.update_cell(20, 8, tables[0]['Jump Shot Range - half court']["Long (3 point jump shots)"][4][:-1])

    sheet.update_cell(22, 7, tables[2][30])
    sheet.update_cell(23, 7, str(100 * float(tables[2][5]) / float(tables[2][15])) + '%')

    steal = float(tables[2][8])
    block = float(tables[2][10])
    def_poss = float(tables[1]['Overall Defense'][team_name][1])
    sheet.update_cell(24, 7, str(100 * steal / def_poss) + '%')
    sheet.update_cell(25, 7, str(100 * block / def_poss) + '%')

    sheet.update_cell(26, 7, tables[0]['Overall Offense']['Transition'][0])
    sheet.update_cell(27, 7, tables[0]['Overall Offense']['Transition'][10])
    sheet.update_cell(26, 8, tables[0]['Overall Offense']['Transition'][4][:-1])

    # -------

    sheet.update_cell(12, 9, tables[1]['Overall Defense'][team_name][10])
    sheet.update_cell(12, 10, tables[1]['Overall Defense'][team_name][4][:-1])
    sheet.update_cell(13, 9, tables[1]['Overall Defense'][team_name][11])
    sheet.update_cell(15, 9, tables[1]['Overall Defense'][team_name][12])

    sheet.update_cell(16, 9, tables[1]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][0])
    sheet.update_cell(17, 9, tables[1]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][9])
    sheet.update_cell(16, 10, tables[1]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][4][:-1])

    mid_rate = (float(tables[1]['Jump Shot Range - half court']["Short (<17')"][0][:-1]) +
                float(tables[1]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][0][:-1])) / 100
    sheet.update_cell(18, 9, str(
        round(float(tables[1]['Shot Attempt - Half Court']['Jump Shots'][0][:-1]) * mid_rate, 2)) + '%')
    mid_makes = float(tables[1]['Jump Shot Range - half court']["Short (<17')"][7]) + \
                float(tables[1]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][7])
    mid_total = float(tables[1]['Jump Shot Range - half court']["Short (<17')"][8]) + \
                float(tables[1]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][8])
    sheet.update_cell(19, 9, str(round(100 * mid_makes / mid_total, 2)) + '%')
    mid_pct = (int(tables[1]['Jump Shot Range - half court']["Short (<17')"][4][:-1]) +
               int(tables[1]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][4][:-1])) // 2
    sheet.update_cell(18, 10, mid_pct)

    three_rate = float(tables[1]['Shot Attempt - Half Court']['Jump Shots'][0][:-1]) * \
                 float(tables[1]['Jump Shot Range - half court']["Long (3 point jump shots)"][0][:-1]) / 100
    sheet.update_cell(20, 9, str(round(three_rate, 2)) + '%')
    sheet.update_cell(21, 9, tables[1]['Jump Shot Range - half court']["Long (3 point jump shots)"][9])
    sheet.update_cell(20, 10, tables[1]['Jump Shot Range - half court']["Long (3 point jump shots)"][4][:-1])

    sheet.update_cell(26, 9, tables[1]['Overall Defense']['Transition'][0])
    sheet.update_cell(27, 9, tables[1]['Overall Defense']['Transition'][10])
    sheet.update_cell(26, 10, tables[1]['Overall Defense']['Transition'][4][:-1])

    # ----------------------------------------------------------------------------------------------------------

    sheet.update_cell(12, 11, rice[0]['Overall Offense']["Rice Owls"][10])
    sheet.update_cell(12, 12, rice[0]['Overall Offense']["Rice Owls"][4][:-1])
    sheet.update_cell(13, 11, rice[0]['Overall Offense']["Rice Owls"][11])
    sheet.update_cell(14, 11, str(round((float(rice[2][12]) / float(rice[2][11])) * 100, 2)) + '%')
    sheet.update_cell(15, 11, rice[0]['Overall Offense']["Rice Owls"][12])

    sheet.update_cell(16, 11, rice[0]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][0])
    sheet.update_cell(17, 11, rice[0]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][9])
    sheet.update_cell(16, 12, rice[0]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][4][:-1])

    mid_rate = (float(rice[0]['Jump Shot Range - half court']["Short (<17')"][0][:-1]) +
                float(rice[0]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][0][:-1])) / 100
    sheet.update_cell(18, 11, str(
        round(float(rice[0]['Shot Attempt - Half Court']['Jump Shots'][0][:-1]) * mid_rate, 2)) + '%')
    mid_makes = float(rice[0]['Jump Shot Range - half court']["Short (<17')"][7]) + \
                float(rice[0]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][7])
    mid_total = float(rice[0]['Jump Shot Range - half court']["Short (<17')"][8]) + \
                float(rice[0]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][8])
    sheet.update_cell(19, 11, str(round(100 * mid_makes / mid_total, 2)) + '%')
    mid_pct = (int(rice[0]['Jump Shot Range - half court']["Short (<17')"][4][:-1]) +
               int(rice[0]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][4][:-1])) // 2
    sheet.update_cell(18, 12, mid_pct)

    three_rate = float(rice[0]['Shot Attempt - Half Court']['Jump Shots'][0][:-1]) * \
                 float(rice[0]['Jump Shot Range - half court']["Long (3 point jump shots)"][0][:-1]) / 100
    sheet.update_cell(20, 11, str(round(three_rate, 2)) + '%')
    sheet.update_cell(21, 11, rice[0]['Jump Shot Range - half court']["Long (3 point jump shots)"][9])
    sheet.update_cell(20, 12, rice[0]['Jump Shot Range - half court']["Long (3 point jump shots)"][4][:-1])

    sheet.update_cell(22, 11, rice[2][30])
    sheet.update_cell(23, 11, str(100 * float(rice[2][5]) / float(rice[2][15])) + '%')

    steal = float(rice[2][8])
    block = float(rice[2][10])
    def_poss = float(rice[1]['Overall Defense']["Rice Owls"][1])
    sheet.update_cell(24, 11, str(100 * steal / def_poss) + '%')
    sheet.update_cell(25, 11, str(100 * block / def_poss) + '%')

    sheet.update_cell(26, 11, rice[0]['Overall Offense']['Transition'][0])
    sheet.update_cell(27, 11, rice[0]['Overall Offense']['Transition'][10])
    sheet.update_cell(26, 12, rice[0]['Overall Offense']['Transition'][4][:-1])

    # -------
    time.sleep(60)

    sheet.update_cell(12, 13, rice[1]['Overall Defense']["Rice Owls"][10])
    sheet.update_cell(12, 14, rice[1]['Overall Defense']["Rice Owls"][4][:-1])
    sheet.update_cell(13, 13, rice[1]['Overall Defense']["Rice Owls"][11])
    sheet.update_cell(15, 13, rice[1]['Overall Defense']["Rice Owls"][12])

    sheet.update_cell(16, 13, rice[1]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][0])
    sheet.update_cell(17, 13, rice[1]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][9])
    sheet.update_cell(16, 14, rice[1]['Shot Attempt - Half Court']['Around Basket (not Post-Ups)'][4][:-1])

    mid_rate = (float(rice[1]['Jump Shot Range - half court']["Short (<17')"][0][:-1]) +
                float(rice[1]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][0][:-1])) / 100
    sheet.update_cell(18, 13, str(
        round(float(rice[1]['Shot Attempt - Half Court']['Jump Shots'][0][:-1]) * mid_rate, 2)) + '%')
    mid_makes = float(rice[1]['Jump Shot Range - half court']["Short (<17')"][7]) + \
                float(rice[1]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][7])
    mid_total = float(rice[1]['Jump Shot Range - half court']["Short (<17')"][8]) + \
                float(rice[1]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][8])
    sheet.update_cell(19, 13, str(round(100 * mid_makes / mid_total, 2)) + '%')
    mid_pct = (int(rice[1]['Jump Shot Range - half court']["Short (<17')"][4][:-1]) +
               int(rice[1]['Jump Shot Range - half court']["Medium (17' to <3 point line)"][4][:-1])) // 2
    sheet.update_cell(18, 14, mid_pct)

    three_rate = float(rice[1]['Shot Attempt - Half Court']['Jump Shots'][0][:-1]) * \
                 float(rice[1]['Jump Shot Range - half court']["Long (3 point jump shots)"][0][:-1]) / 100
    sheet.update_cell(20, 13, str(round(three_rate, 2)) + '%')
    sheet.update_cell(21, 13, rice[1]['Jump Shot Range - half court']["Long (3 point jump shots)"][9])
    sheet.update_cell(20, 14, rice[1]['Jump Shot Range - half court']["Long (3 point jump shots)"][4][:-1])

    sheet.update_cell(26, 13, rice[1]['Overall Defense']['Transition'][0])
    sheet.update_cell(27, 13, rice[1]['Overall Defense']['Transition'][10])
    sheet.update_cell(26, 14, rice[1]['Overall Defense']['Transition'][4][:-1])


def main():
    team = "Florida International Panthers"
    sheet_name = '2/19 @ FIU'

    data = teamData(team)
    tables = []
    for i in range(2):
        tables.append(process_data(data[i]))
    tables.append(process_box(data[2]))
    opp_players = player_names(tables)

    rice = teamData("Rice Owls")
    rtables = []
    for i in range(2):
        rtables.append(process_data(rice[i]))
    rtables.append(process_box(rice[2]))
    rplayers = player_names(rtables)

    google(tables, rtables, sheet_name, team)
    
# get player names given a table for each team
def player_names(tables):
    e = list(tables[0]['Overall'].keys())[1:]
    names = []
    for i in e:
        if len(i) != 0:
            names.append(" ".join(i.split()[1:]))
    return [e, names]


if __name__ == "__main__":
    main()
