from collections import Counter
import numpy as np
import pandas as pd
import Tier_Pull
import time

pd.options.mode.chained_assignment = None

""""""


def df_load():
    """
    Loads the file names to dataframes
    """

    df = Tier_Pull.read_xlsx_file(r"\\newco.global\newcoroot\Global\EMEA\userdir$"
                                  r"\o_boom\Oliver\LC_Counterparty_Analysis.xlsx",
                                  "Performance")

    df_ranking = Tier_Pull.read_xlsx_file(r"\\newco.global\newcoroot\Global\EMEA\userdir$"
                                          r"\o_boom\Oliver\LC_Counterparty_Analysis.xlsx",
                                          "Tier Ranking")

    df_tier_change = Tier_Pull.read_xlsx_file(r"\\newco.global\newcoroot\Global\EMEA\userdir$"
                                              r"\o_boom\Oliver\LC_Counterparty_Analysis.xlsx",
                                              "Tier Changes")

    return df, df_ranking, df_tier_change


def target_LP_LC(df):
    """
    For each LP/LC combination for entitlement added/intiialized rows
    conducts metric analysis on each row and writes the information to
    the tier change dataframe for later operations and analysis
    """
    sweep_list = df['Sweep'].unique()

    for sweep in sweep_list:

        filter_sweep = df.loc[(df['Sweep'] == sweep)]
        LC_list = filter_sweep['LC_ACCOUNT'].unique()

        for LC in LC_list:

            filter_LC = df.loc[(df['LC_ACCOUNT'] == LC) & (df['STATUS'] != 'Entitlement removed')]
            LP_list = filter_LC['LP Floor ID'].unique()

            for LP in LP_list:

                filter_LP = filter_LC.loc[(filter_LC['LP Floor ID'] == LP)]
                ADV_add(filter_LP)
                metric_analyser(filter_LP)

                for index, row in filter_LP.iterrows():
                    df.loc[(df['TIME'] == row['TIME']) &
                           (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                           (df['LP Floor ID'] == row['LP Floor ID']), 'ADV'] = filter_LP['ADV']
                    df.loc[(df['TIME'] == row['TIME']) &
                           (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                           (df['LP Floor ID'] == row['LP Floor ID']), 'ADV Change'] = filter_LP['ADV Change']
                    df.loc[(df['TIME'] == row['TIME']) &
                           (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                           (df['LP Floor ID'] == row['LP Floor ID']), 'M2M Change'] = filter_LP['M2M Change']
                    df.loc[(df['TIME'] == row['TIME']) &
                           (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                           (df['LP Floor ID'] == row['LP Floor ID']), 'MI Change'] = filter_LP['MI Change']
                    df.loc[(df['TIME'] == row['TIME']) &
                           (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                           (df['LP Floor ID'] == row['LP Floor ID']), 'LP Reject % Change'] = filter_LP[
                        'LP Reject % Change']
                    df.loc[(df['TIME'] == row['TIME']) &
                           (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                           (df['LP Floor ID'] == row['LP Floor ID']), 'ALPHA Change'] = filter_LP['ALPHA Change']
                    df.loc[(df['TIME'] == row['TIME']) &
                           (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                           (df['LP Floor ID'] == row['LP Floor ID']),
                           'Tier Change Impact'] = filter_LP['Tier Change Impact']
    return df


def ADV_add(df):
    """
    Calculated the average daily volume for each row
    """

    df_operate = df.reset_index()
    for index, row in df_operate.iterrows():
        ADV = (row['Traded Vol (m)']) / (row['Duration'])

        df.loc[(df['TIME'] == row['TIME']) &
               (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ADV'] = ADV
    return


def metric_analyser(df):
    """
    Compares tiers for each LP/LC combination and returns the relative performance of
    a tier compared to the previous tier for average daily volume, marked to market, market
    impact, LP rejection percentage, alpha and the overall improvement/degrading of performance
    for that tier If/elif/else statements are quite longwinded by effectively repeat themselves
    over so understanding one will do the same for others, would have turned them into a function
    but some nuances meant it would have been equally long winded
    """

    df_operate = df.reset_index()
    for index, row in df_operate.iterrows():
        if index > 0:

            if df_operate['ADV'][index] > df_operate['ADV'][(index - 1)]:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ADV change'] = 1
            elif df_operate['ADV'][index] < df_operate['ADV'][(index - 1)]:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ADV Change'] = -1
            elif (df_operate['ADV'][index] == df_operate['ADV'][(index - 1)] and
                  df_operate['ADV'][index] != np.nan):
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ADV Change'] = 0
            else:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ADV Change'] = np.nan

            if df_operate['MarkToMid 0s'][index] < df_operate['MarkToMid 0s'][(index - 1)]:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'M2M Change'] = 1
            elif df_operate['MarkToMid 0s'][index] > df_operate['MarkToMid 0s'][(index - 1)]:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'M2M Change'] = -1
            elif (df_operate['MarkToMid 0s'][index] == df_operate['MarkToMid 0s'][(index - 1)] and
                  df_operate['MarkToMid 0s'][index] != np.nan):
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'M2M Change'] = 0
            else:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'M2M Change'] = np.nan

            if df_operate['EBS Avg. MI 30s'][index] < df_operate['EBS Avg. MI 30s'][(index - 1)]:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'MI Change'] = 1
            elif df_operate['EBS Avg. MI 30s'][index] > df_operate['EBS Avg. MI 30s'][(index - 1)]:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'MI Change'] = -1
            elif (df_operate['EBS Avg. MI 30s'][index] == df_operate['EBS Avg. MI 30s'][(index - 1)] and
                  df_operate['EBS Avg. MI 30s'][index] != np.nan):
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'MI Change'] = 0
            else:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'MI Change'] = np.nan

            if df_operate['LP Reject %'][index] < df_operate['LP Reject %'][(index - 1)]:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'LP Reject % Change'] = 1
            elif df_operate['LP Reject %'][index] > df_operate['LP Reject %'][(index - 1)]:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'LP Reject % Change'] = -1
            elif (df_operate['LP Reject %'][index] == df_operate['LP Reject %'][(index - 1)] and
                  df_operate['LP Reject %'][index] != np.nan):
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'LP Reject % Change'] = 0
            else:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'LP Reject % Change'] = np.nan

            if df_operate['Net Alpha (USD per mil)'][index] > df_operate['Net Alpha (USD per mil)'][(index - 1)]:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ALPHA Change'] = 1
            elif df_operate['Net Alpha (USD per mil)'][index] < df_operate['Net Alpha (USD per mil)'][(index - 1)]:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ALPHA Change'] = -1
            elif (df_operate['Net Alpha (USD per mil)'][index] == df_operate['Net Alpha (USD per mil)'][(index - 1)] and
                  df_operate['Net Alpha (USD per mil)'][index] != np.nan):
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ALPHA Change'] = 0
            else:
                df.loc[(df['TIME'] == row['TIME']) &
                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ALPHA Change'] = np.nan

            row['Tier Change Impact'] = np.nansum([row['ADV Change'],
                                                   row['M2M Change'],
                                                   row['MI Change'],
                                                   row['LP Reject % Change'],
                                                   row['ALPHA Change']])
            df.loc[(df['TIME'] == row['TIME']) &
                   (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'Tier Change Impact'] = row['Tier Change Impact']

        else:
            df.loc[(df['TIME'] == row['TIME']) &
                   (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ADV Change'] = np.nan
            df.loc[(df['TIME'] == row['TIME']) &
                   (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'M2M Change'] = np.nan
            df.loc[(df['TIME'] == row['TIME']) &
                   (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'MI Change'] = np.nan
            df.loc[(df['TIME'] == row['TIME']) &
                   (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'LP Reject % Change'] = np.nan
            df.loc[(df['TIME'] == row['TIME']) &
                   (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'ALPHA Change'] = np.nan
            df.loc[(df['TIME'] == row['TIME']) &
                   (df['LC_ACCOUNT'] == row['LC_ACCOUNT']), 'Tier Change Impact'] = np.nan

    return df


def excel_writer(df, df2):
    path = r"\\newco.global\newcoroot\Global\EMEA\userdir$\o_boom\Oliver\LC_Counterparty_Met.xlsx"
    writer = pd.ExcelWriter(path)
    df.to_excel(writer, sheet_name='Tier Change', index=False)
    df2.to_excel(writer, sheet_name='Recommended Tiers', index=False)
    writer.save()
    writer.close()
    return


def verdict(df):
    """
    Looks at overall tier change impact for certain
    criteria and provides quick insight for the analyst
    """
    sweep_list = df['Sweep'].unique()

    for sweep in sweep_list:
        filter_sweep = df.loc[(df['Sweep'] == sweep)]
        LC_list = filter_sweep['LC_ACCOUNT'].unique()

        for LC in LC_list:

            filter_LC = df.loc[(df['LC_ACCOUNT'] == LC) & (df['STATUS'] != 'Entitlement removed')]
            LP_list = filter_LC['LP Floor ID'].unique()

            for LP in LP_list:
                filter_LP = filter_LC.loc[(filter_LC['LP Floor ID'] == LP)]

                for index, row in filter_LP.iterrows():

                    if (row['Duration'] > 3) and row['Tier Change Impact'] == 5:
                        df.loc[(df['TIME'] == row['TIME']) &
                               (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df['STATUS'] == row['STATUS']), 'Verdict'] = 'Good Change'
                    elif (row['Duration'] > 3) and row['Tier Change Impact'] == -5:
                        df.loc[(df['TIME'] == row['TIME']) &
                               (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df['STATUS'] == row['STATUS']), 'Verdict'] = 'Bad Change'
                    elif (row['Duration'] > 3) and row['Tier Change Impact'] == 0:
                        df.loc[(df['TIME'] == row['TIME']) &
                               (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df['STATUS'] == row['STATUS']), 'Verdict'] = 'Neutral Change/No information'
                    elif row['Duration'] < 3:
                        df.loc[(df['TIME'] == row['TIME']) &
                               (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df['STATUS'] == row['STATUS']), 'Verdict'] = 'Too Short'
    return df


def most_common_in_list(lst):
    data = Counter(lst)
    return data.most_common(1)[0][0]


def best_rank(df):
    """
    Finds the best performing tier in each criteria, then ranks
    the tiers to recommend the tier that the LC should be on
    """

    col_names = ['LP_ACCOUNT', 'LC_ACCOUNT', 'Sweep', 'Best Tier', 'Level']
    df_best_tier = pd.DataFrame(columns=col_names)
    sweep_list = df['Sweep'].unique()

    for sweep in sweep_list:
        filter_sweep = df.loc[(df['Sweep'] == sweep)]
        LC_list = filter_sweep['LC_ACCOUNT'].unique()

        for LC in LC_list:

            filter_LC = filter_sweep.loc[(df['LC_ACCOUNT'] == LC) & (filter_sweep['STATUS'] != 'Entitlement removed')]
            LP_list = filter_LC['LP Floor ID'].unique()

            for LP in LP_list:
                '''
                Want to conduct only if values in column
                '''

                filter_LP = filter_LC.loc[(filter_LC['LP Floor ID'] == LP) & (filter_LC['Duration'] > 3)]

                filter_LP.dropna(subset=['ADV', 'M2M Change', 'EBS Avg. MI 30s',
                                         'LP Reject %', 'Net Alpha (USD per mil)'], how='all', inplace=True)

                if len(filter_LP) > 1:

                    ADV = filter_LP.sort_values(by='ADV', ascending=False)
                    M2M = filter_LP.sort_values(by='M2M Change')
                    MI = filter_LP.sort_values(by='EBS Avg. MI 30s')
                    REJ = filter_LP.sort_values(by='LP Reject %')
                    ALPHA = filter_LP.sort_values(by='Net Alpha (USD per mil)', ascending=False)

                    index_list = [ADV.index[0], M2M.index[0], MI.index[0], REJ.index[0], ALPHA.index[0]]
                    best_tier = most_common_in_list(index_list)
                    best_tier_count = index_list.count(best_tier)

                    target = df.iloc[best_tier]

                    if best_tier_count > 1:
                        row = [LP, LC, target['Sweep'], target['Ranking'], best_tier_count]
                        df_best_tier.loc[len(df_best_tier)] = row
                    else:
                        row = [LP, LC, np.nan, 'No Best Tier', np.nan]
                        df_best_tier.loc[len(df_best_tier)] = row
    return df_best_tier


def main():
    start_time_TM = time.clock()

    df_performance, df_ranking, df_tier_change = df_load()

    df_tier_change = target_LP_LC(df_tier_change)
    print(time.clock() - start_time_TM, "seconds")
    """
    Currenttly index compared with index infront so does not work for the single rowed intial index
    """

    df_tier_change = verdict(df_tier_change)

    df_best_tier = best_rank(df_tier_change)
    print(time.clock() - start_time_TM, "seconds")

    excel_writer(df_tier_change, df_best_tier)

    print(time.clock() - start_time_TM, "seconds")


if __name__ == '__main__':
    main()

'''
Next task is to look at the added/removed criteria
'''
