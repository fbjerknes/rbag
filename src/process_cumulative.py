import pygsheets
import pandas as pd
import datetime

API_CRED_LOCATION = "C:/study zone/Rice/DOSA/Google Sheets API/client_secret.json"
SHEET_NAME = "Lineup Efficiency 19-20"
# Index starts with 0, so if the worksheet is the first, index you enter below should be 0
CUMULATIVE_WORKSHEET_INDEX = 2
# Why not just override the cumulative worksheet? Because there is really no way to format it beautifully from here, so
# we generate output to a new worksheet and copy paste it to our beautifully formatted cumulative worksheet
# More importantly, if the code goes wrong, our cumulative sheet does not get destroyed.
NEW_WORKSHEET_INDEX = 3


def process_cumulative_lineup_efficiency(api_cred_location, sheet_name, cumulative_worksheet_index,
                                         new_worksheet_index) -> None:
    """
    process data of a single game:
    merge identical lineups, calculate duration, frequency, plus minus, update it to google sheet
    Note: upload new cumulative data BUT DOES NOT update our cumulative sheet for safety purpose
    :param cumulative_worksheet_index: integer index of worksheet containing the cumulative data
    :param api_cred_location: string of file loc
    :param sheet_name:  string of google sheet name (not the worksheet)
    :param new_worksheet_index: integer index of worksheet want to be updated to
    :return:
    """
    # use creds to create a client to interact with the Google Drive API
    client = pygsheets.authorize(service_file=api_cred_location)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here. and count up the index of the sheet containing the raw data
    sheet = client.open(sheet_name)[cumulative_worksheet_index]

    # Convert to pd.dataframe
    df = pd.DataFrame(sheet.get_values(start=(1, 2), end=(100, 10), returnas='matrix'),
                      columns=["pg", "sg", "sf", "pf", "c",
                               "initials", "duration", "plus_minus", "frequency"])
    # drop first row
    df = df.drop(df.index[[0]])
    print(len(df))

    # convert string into time for processing
    time = list(df["duration"])
    time = [datetime.timedelta(minutes = int(t.split(":")[1])) + datetime.timedelta(seconds=int(t.split(":")[2])) for t in time]

    # Get durations
    df["duration"] = time
    temp_df = df.drop(columns = ['frequency', 'plus_minus', 'pg','sg','sf','pf','c'])
    durations = list(temp_df.groupby(by=["initials"]).sum()["duration"])

    # Why convert these to number now? If we do it before we do sum on duration, then it does not
    # add the timedelta object up This is probably due to their dynamic dispatching that pandas do, but I am not sure
    df["plus_minus"] = df["plus_minus"].astype(int)
    df["frequency"] = df["frequency"].astype(int)

    # Split up the initials
    cleaned_df = pd.DataFrame(df.groupby(by=["initials"]).sum())
    cleaned_df["duration"] = durations
    cleaned_df["duration"] = "00:"+cleaned_df["duration"].astype(str).str[-15:-10]
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
    cleaned_df["initials"] = initials
    cleaned_df["pg"] = pg
    cleaned_df["sg"] = sg
    cleaned_df["sf"] = sf
    cleaned_df["pf"] = pf
    cleaned_df["c"] = c

    columns = ["pg", "sg", "sf", "pf", "c", "initials", "duration", "plus_minus", "frequency"]
    cleaned_df = cleaned_df.reindex(columns, axis='columns')
    cleaned_df = cleaned_df.rename(columns={"plus_minus": " +/-", "pg": "Lineup"})
    sorted_df = cleaned_df.sort_values(by=[" +/-"], ascending=False)
    print(sorted_df.head())

    new_sheet = client.open("Lineup Efficiency 19-20")[new_worksheet_index]
    new_sheet.set_dataframe(sorted_df, (3, 1))
    print(len(sorted_df))
    print("Successfully uploaded cumulative lineup efficiency to" + sheet_name)


process_cumulative_lineup_efficiency(API_CRED_LOCATION, SHEET_NAME, CUMULATIVE_WORKSHEET_INDEX, NEW_WORKSHEET_INDEX)