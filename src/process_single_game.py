import pygsheets
import pandas as pd
import datetime

API_CRED_LOCATION = "C:/study zone/Rice/DOSA/Google Sheets API/client_secret.json"
SHEET_NAME = "Lineup Efficiency 19-20"
# Index starts with 0, so if the worksheet is the first, index you enter below should be 0
RAW_WORKSHEET_INDEX = None
NEW_WORKSHEET_INDEX = None


def process_single_game_lineup_efficiency(api_cred_location, sheet_name, raw_worksheet_index,
                                          new_worksheet_index) -> None:
    """
    process data of a single game:
    merge identical lineups, calculate duration, frequency, plus minus, update it to google sheet
    Note: Does not update any cumulative (only single game)!!!
    :param api_cred_location: string of file loc
    :param sheet_name:  string of google sheet name (not the worksheet)
    :param raw_worksheet_index: integer index of worksheet containing the raw data
    :param new_worksheet_index: integer index of worksheet want to be updated to
    :return:
    """
    # use creds to create a client to interact with the Google Drive API
    client = pygsheets.authorize(service_file=api_cred_location)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here. and count up the index of the sheet containing the raw data
    sheet = client.open(sheet_name)[raw_worksheet_index]

    # Convert to pd.dataframe
    df = pd.DataFrame(sheet.get_values(start=(1, 1), end=(30, 10), returnas='matrix'),
                      columns=["initials", "pg", "sg", "sf", "pf", "c", "half", "time", "plus_minus", "frequency"])

    # drop first 2 rows
    df = df.drop(df.index[[0, 1]])

    # convert string into time for processing
    end_time = list(df["time"])
    end_time = [datetime.time(0, int(et.split(":")[1]), int(et.split(":")[2])) for et in end_time]
    half = [int(h) for h in df["half"]]

    # create a list of start time
    start_time = [datetime.time(0, 20, 0)]
    for index in range(len(end_time)):
        if half[index] == 1 and half[index + 1] == 2:
            start_time.append(datetime.time(0, 20, 0))
        else:
            start_time.append(end_time[index])

    # process times
    today = datetime.date.today()
    durations = [(datetime.datetime.combine(today, start) - datetime.datetime.combine(today, end))
                 for start, end in zip(start_time, end_time)]
    # Get durations
    df["duration"] = durations
    durations = list(df.groupby(by=["initials", "pg", "sg", "sf", "pf", "c"]).sum()["duration"])

    # Why convert these to number now? If we do it before we do sum on duration, then it does not
    # add the timedelta object up This is probably due to their dynamic dispatching that pandas do, but I am not sure
    df["Plus_minus"] = df["plus_minus"].astype(int)
    df["Frequency"] = df["frequency"].astype(int)

    # Split up the initials
    cleaned_df = pd.DataFrame(df.groupby(by=["initials"]).sum())
    cleaned_df["Duration"] = durations
    cleaned_df["Duration"] = "00:" + cleaned_df["Duration"].astype(str).str[-15:-10]
    initials = []
    pg = []
    sg = []
    sf = []
    pf = []
    c = []

    for ini, one, two, three, four, five in df.groupby(by=["initials", "pg", "sg", "sf", "pf", "c"]).groups.keys():
        initials.append(str(ini))
        pg.append(one)
        sg.append(two)
        sf.append(three)
        pf.append(four)
        c.append(five)

    # Update/Add all columns we want
    cleaned_df["Initials"] = initials
    cleaned_df["PG"] = pg
    cleaned_df["SG"] = sg
    cleaned_df["SF"] = sf
    cleaned_df["PF"] = pf
    cleaned_df["C"] = c

    columns = ["PG", "SG", "SF", "PF", "C", "Initials", "Duration", "Plus_minus", "Frequency"]
    cleaned_df = cleaned_df.reindex(columns, axis='columns')
    cleaned_df = cleaned_df.rename(columns={"Plus_minus": " +/-", "PG": "Lineup"})
    sorted_df = cleaned_df.sort_values(by=[" +/-"], ascending=False)
    print(sorted_df.head())

    new_sheet = client.open("Lineup Efficiency 19-20")[new_worksheet_index]
    new_sheet.set_dataframe(sorted_df, (1, 1))
    print("Successfully created clean worksheet")


process_single_game_lineup_efficiency(API_CRED_LOCATION, SHEET_NAME, RAW_WORKSHEET_INDEX, NEW_WORKSHEET_INDEX)