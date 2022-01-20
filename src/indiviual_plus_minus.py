import pygsheets
import pandas as pd

API_CRED_LOCATION = "C:/study zone/Rice/DOSA/Google Sheets API/client_secret.json"
LINEUP_EFFICIENCY_SHEET_NAME = "Lineup Efficiency 19-20"
# Index starts with 0, so if the worksheet is the first, index you enter below should be 0
# The sheet should contain the RAW (not cleaned) data
LINEUP_EFFICIENCY_WORKSHEET_INDEX = None
# This is the plus minus worksheet you want the output to be in
PLUS_MINUS_SHEET_NAME = "Individual +/- 19-20"
PLUS_MINUS_WORKSHEET_INDEX = None
# The list of players' name in the same order as we wanted it in the plus minus sheet
PLAYER_LIST = ["PM", "JP", "TM", "AA", "QO", "AO", "RM", "BM", "TMC", "RMY", "MF", "ZC", "DP", "CM", "TH"]


def process_single_game_lineup_efficiency(api_cred_location, plus_minus_sheet_name, lineup_efficiency_name,
                                          lineup_worksheet_index, plus_minus_worksheet_index, player_list) -> None:
    """
    process data of a single game:
    merge identical lineups, calculate duration, frequency, plus minus, update it to google sheet
    Note: Does not update any cumulative (only single game)!!!
    :param player_list: list of strings representing players' name in the order appeared in the worksheet
    :param lineup_efficiency_name: string of the google sheet name
    :param plus_minus_sheet_name: string of the google sheet name
    :param lineup_worksheet_index: zero-indexed integer for the worksheet containing the RAW (not cleaned) data
    :param plus_minus_worksheet_index: zero-indexed integer for the worksheet we want our output to be in
    :param api_cred_location: string of file loc
    :return:
    """
    # use creds to create a client to interact with the Google Drive API
    client = pygsheets.authorize(service_file=api_cred_location)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here. and count up the index of the sheet containing the raw data
    sheet = client.open(lineup_efficiency_name)[lineup_worksheet_index]

    # Convert to pd.dataframe
    df = pd.DataFrame(sheet.get_values(start=(1, 1), end=(30, 10), returnas='matrix'),
                      columns=["initials", "pg", "sg", "sf", "pf", "c", "half", "time", "plus_minus", "frequency"])

    # drop first 2 rows
    df = df.drop(df.index[[0, 1]])

    # drop unwanted columns
    df = df.drop(columns=["initials", "time", "frequency"])

    # plus minus should be type integer instead of string
    df["plus_minus"] = df["plus_minus"].astype(int)

    # joining columns to a list of tuples, something I am more familiar at handling
    pg = list(df["pg"])
    sg = list(df["sg"])
    sf = list(df["sf"])
    pf = list(df["pf"])
    c = list(df["c"])
    half = list(df["half"])
    plus_minus = list(df["plus_minus"])
    lineup_and_half = list(zip(pg, sg, sf, pf, c, half, plus_minus))

    individual_plus_minus_first_half = [0] * len(player_list)
    individual_plus_minus_second_half = [0] * len(player_list)
    # The list of our players' names mapped to their initials
    for i in range(len(player_list)):
        for pg, sg, sf, pf, c, half, plus_minus in lineup_and_half:
            # check if the player played in this half
            if half == "1" and (player_list[i] == pg or player_list[i] == sg or player_list[i] == sf or
                                player_list[i] == pf or player_list[i] == c):
                individual_plus_minus_first_half[i] += plus_minus
            elif half == "2" and (player_list[i] == pg or player_list[i] == sg or player_list[i] == sf or
                                  player_list[i] == pf or player_list[i] == c):
                individual_plus_minus_second_half[i] += plus_minus

    plus_minus = pd.DataFrame(columns=["1st half +/-", "2nd half +/-"],
                              data=list(zip(individual_plus_minus_first_half, individual_plus_minus_second_half)))

    new_sheet = client.open(plus_minus_sheet_name)[plus_minus_worksheet_index]
    new_sheet.set_dataframe(plus_minus, (2, 3))
    print("Successfully uploaded plus minus for the game")


process_single_game_lineup_efficiency(API_CRED_LOCATION, PLUS_MINUS_SHEET_NAME, LINEUP_EFFICIENCY_SHEET_NAME,
                                      LINEUP_EFFICIENCY_WORKSHEET_INDEX, PLUS_MINUS_WORKSHEET_INDEX, PLAYER_LIST)
