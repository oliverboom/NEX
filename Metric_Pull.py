from collections import Counter
import datetime
import openpyxl
import numpy as np
import pandas as pd
import datetime
# pd.options.mode.chained_assignment = None
import Tier_Pull
import Tier_Analysis
import time


def df_load():
    """
    Loads the file names to dataframes
    """

    df_tier_changes = Tier_Pull.read_xlsx_file(r"\\newco.global\newcoroot\Global\EMEA\userdir$"
                                               r"\o_boom\Oliver\LC_Counterparty_Analysis.xlsx",
                                               "Tier Changes")

    df_kdb = Tier_Pull.read_xlsx_file(r"\\newco.global\newcoroot\Global\EMEA\userdir$"
                                      r"\o_boom\Oliver\KDB_TIER_INFO.xlsx",
                                      "KDB_TIER_INFO")

    return df_tier_changes, df_kdb


def time_and_date_priming_kdb(df):
    df['startDate'] = df['startDate'].str.replace('.', '-')
    df["TIME"] = df['startDate'] + ' ' + df["startTime"].astype(str).str[0:8]
    return df


def time_and_date_priming_tier_change(df):
    df["TIME"] = df['TIME'].astype(str).str[0:19]
    return df


def currency_primer(df):
    df['CCY_PAIR'] = df['CCY_PAIR'].str.replace('/', '')
    df['CCY_PAIR'] = df['CCY_PAIR'].str[3:]
    return df



def row_of_interest(df_tier_change, df_kdb):
    for index, row in df_tier_change.iterrows():

        target_row = df_kdb.loc[(df_kdb['TIME'] == row['TIME']) &
                                (df_kdb['counterParty'] == row['LP_ACCOUNT']) &
                                (df_kdb['floorCode'] == row['LC_ACCOUNT']) &
                                (df_kdb['symList'] == row['CCY_PAIR'])]
        target_row = target_row.fillna('NA')

        if not target_row.empty:
            df_tier_change.loc[(df_tier_change['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                               (df_tier_change['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df_tier_change['STATUS'] == 'Entitlement added') &
                               (df_tier_change['TIME'] == row['TIME']),
                               'Traded Vol (m)'] = target_row['baseDeals']

            df_tier_change.loc[(df_tier_change['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                               (df_tier_change['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df_tier_change['STATUS'] == 'Entitlement added') &
                               (df_tier_change['TIME'] == row['TIME']),
                               'MarkToMid 0s'] = target_row['baseDeals']

            df_tier_change.loc[(df_tier_change['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                               (df_tier_change['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df_tier_change['STATUS'] == 'Entitlement added') &
                               (df_tier_change['TIME'] == row['TIME']),
                               'EBS Avg. MI 30s'] = target_row['ERR']

            df_tier_change.loc[(df_tier_change['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                               (df_tier_change['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df_tier_change['STATUS'] == 'Entitlement added') &
                               (df_tier_change['TIME'] == row['TIME']),
                               'LP Rejects'] = target_row['LPRej']

            df_tier_change.loc[(df_tier_change['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                               (df_tier_change['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df_tier_change['STATUS'] == 'Entitlement added') &
                               (df_tier_change['TIME'] == row['TIME']),
                               'Net Alpha (USD per mil)'] = target_row['aMil']

    return df_tier_change


def excel_writer(df):
    path = r"\\newco.global\newcoroot\Global\EMEA\userdir$\o_boom\Oliver\LC_Counterparty_Pull.xlsx"
    writer = pd.ExcelWriter(path)
    df.to_excel(writer, sheet_name='Tier Change with Metrics', index=False)
    writer.save()
    writer.close()
    return


def main():
    start_time = time.clock()

    df_tier_changes, df_kdb = df_load()

    df_kdb = time_and_date_priming_kdb(df_kdb)
    df_tier_changes = time_and_date_priming_tier_change(df_tier_changes)

    df_tier_changes = currency_primer(df_tier_changes)
    df_tier_change = row_of_interest(df_tier_changes, df_kdb)

    excel_writer(df_tier_change)

    print(time.clock() - start_time, "seconds")


if __name__ == '__main__':
    main()
