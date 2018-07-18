import pandas as pd
import time
import numpy as np
pd.options.mode.chained_assignment = None

'''
README

Make sure that the read file and write file locations are pointed
at the desired location, that the appropriate sheet names are given
With python if writing the path name the backslash is an escape
character so make sure that you have r in front of the string to indicate 
it is to be interpreted as a raw string
'''


def read_csv_file(file_location):
    df = pd.read_csv(file_location, engine='python', error_bad_lines=False)
    return df


def read_xlsx_file(file_location, sheet):
    df = pd.read_excel(file_location, sheet_name=sheet)
    return df


def df_reformater(original_df):
    """ Taking string format and turning into floats"""
    counter = 0
    new_df = []

    if not isinstance(original_df.iloc[0], float):

        for element in original_df:
            counter += 1

            if ',' in element:
                element = element.replace(',', '')

            new_df.append(float(element))

        return new_df

    else:
        return original_df


def check_vol_name(df):
    """
    Sometimes code returns different names
    for traded volume. This function
    prevents errors
    """

    cols = list(df)

    for item in cols:

        if 'Traded Vol' in item:
            traded_vol = item
            return traded_vol

    print('No Traded Vol Column')
    return


def split_string(df, str_2_split, beginning, split_location, end, index1, index2):
    """ Splitting Out String"""

    df[index1] = str_2_split.str[beginning:split_location]
    df[index2] = str_2_split.str[split_location:end]
    cols = list(df)

    if cols[0] == 'LP FloorCode':
        cols.insert(1, cols.pop(cols.index(index1)))
        cols.insert(2, cols.pop(cols.index(index2)))
    else:
        cols.insert(0, cols.pop(cols.index(index1)))
        cols.insert(1, cols.pop(cols.index(index2)))

    df = df.ix[:, cols]
    return df


def sort_values(df):
    df.sort_values(by=['LP Floor ID', 'MarkToMid 0s'], ascending=[True, True], inplace=True)
    return df


def ranking(df):
    """
    Returns the relative ranking of the tiers by Marked to Middle
    spread for select and non select tiers
    """

    df_non_select = df.loc[df.index.astype(str).str[0] == 'Z']
    df_non_select = sort_values(df_non_select)

    rank_name = ['Platinum', 'Gold', 'Silver', 'Bronze',
                 'Steel', 'Aluminium', 'Copper', 'Tin',
                 'Wood', 'Sand', 'Water', 'Air', 'Polluted Air',
                 'Muddy Water']

    LP_list = df_non_select['LP Floor ID'].unique()

    for LP in LP_list:

        unique_LP = df_non_select.loc[df_non_select['LP Floor ID'] == LP]
        count_alpha = 0
        count_number = 0

        for index, row in unique_LP.iterrows():

            if row['Tier Code'].isalpha():
                df_non_select.loc[(df_non_select['LP InstCode'] == row['LP InstCode']) &
                                  (df_non_select['LP Region'] == row['LP Region']) &
                                  (df_non_select['MarkToMid 0s'] == row['MarkToMid 0s']),
                                  'Ranking'] = rank_name[count_alpha]

                count_alpha += 1
            else:
                df_non_select.loc[(df_non_select['LP InstCode'] == row['LP InstCode']) &
                                  (df_non_select['LP Region'] == row['LP Region']) &
                                  (df_non_select['MarkToMid 0s'] == row['MarkToMid 0s']),
                                  'Ranking'] = rank_name[count_number]

                count_number += 1

    df_select = df.loc[df.index.astype(str).str[0] != 'Z']
    inst_code_list = df_select['LP InstCode'].unique()

    for institution in inst_code_list:

        unique_inst = df_select.loc[df_select['LP InstCode'] == institution]
        LP_region_list = unique_inst['LP Region'].unique()

        for LP_region in LP_region_list:

            unique_LP_region = unique_inst.loc[unique_inst['LP Region'] == LP_region]
            unique_LP_region.sort_values(by=['MarkToMid 0s'], ascending=[True], inplace=True)
            count = 0

            for index, row in unique_LP_region.iterrows():
                df_select.loc[(df_select['LP InstCode'] == row['LP InstCode']) &
                              (df_select['LP Region'] == row['LP Region']) &
                              (df_select['MarkToMid 0s'] == row['MarkToMid 0s']),
                              'Ranking'] = rank_name[count]
                count += 1

    return df_non_select, df_select


def print_pandas(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', 20):
        print(df)


def df_filter(df, filter_column, filter_value):
    df = df[df[filter_column].str.contains(filter_value, na=False)]
    return df


def add_column(df_performance, df_ranking, col_name):
    for index, row in df_ranking.iterrows():
        target_LP = df_performance.loc[df_performance['LP Floor ID'] == row['LP Floor ID']]

        LP_column_to_add = target_LP[col_name].get_values()

        df_ranking.loc[(df_ranking['LP Floor ID'] == row['LP Floor ID']),
                       col_name] = LP_column_to_add
    return df_ranking


def write_files(df, df_ranking, df_tier_change):
    write_location = pd.ExcelWriter(r"\\newco.global\newcoroot\Global\EMEA"
                                    r"\userdir$\o_boom\Oliver\LC_Counterparty_Out.xlsx")

    df.to_excel(write_location, 'Performance')
    df_ranking.to_excel(write_location, 'Tier Ranking')
    df_tier_change.to_excel(write_location, 'Tier Changes', index=False)

    write_location.save()
    return


def main():
    start_time_TP = time.clock()

    df_performance = read_csv_file(r"\\newco.global\newcoroot\Global\EMEA\userdir$\o_boom\Oliver\LC_Counterparty.csv")

    df_tier_change = read_xlsx_file(r"\\newco.global\newcoroot\Global\EMEA\userdir$"
                                    r"\o_boom\Oliver\LPM_past_6_months - Copy.xlsx",
                                    'Export Worksheet')

    '''
    Splitting out the Floor code
    To make it concatenate-able
    Then concatenating
    '''

    df_performance = split_string(df_performance,
                                  df_performance["LP FloorCode"].astype(str),
                                  0, 3, 4, 'LP Floor ID', 'Tier Code')

    df_performance['MarkToMid 0s'] = df_reformater(df_performance['MarkToMid 0s'])

    traded_vol = check_vol_name(df_performance)
    df_performance[traded_vol] = df_reformater(df_performance[traded_vol])

    df_floor_code = df_performance.groupby(['LP FloorCode']).agg({'MarkToMid 0s': np.mean, traded_vol: np.sum})

    '''
    Same again but need to use index
    instead of column for this time
    '''

    df_ranking = split_string(df_floor_code, df_floor_code.index, 0, 3, 4, 'LP Floor ID', 'Tier Code')

    add_column(df_performance, df_ranking, 'LP InstCode')
    add_column(df_performance, df_ranking, 'LP Region')

    df_non_select, df_select = ranking(df_ranking)

    df_ranking = pd.concat([df_non_select, df_select])

    '''
    Write dataframe information to xlsx
    '''

    df_tier_change = df_filter(df_tier_change, 'CCY_PAIR', 'SP.EUR/USD')
    df_added = df_filter(df_tier_change, 'STATUS', 'Entitlement added')
    df_removed = df_filter(df_tier_change, 'STATUS', 'Entitlement removed')

    df_tier_change = pd.concat([df_added, df_removed])

    df_tier_change = split_string(df_tier_change, df_tier_change["LP_TIER"].astype(str),
                                  0, 3, 4, 'LP Floor ID', 'Tier Code')

    write_files(df_performance, df_ranking, df_tier_change)

    print(time.clock() - start_time_TP, "seconds")


if __name__ == '__main__':
    main()
