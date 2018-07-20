import exe
import pandas as pd
import Tier_Pull
import time

pd.options.mode.chained_assignment = None

"""
When importing the KDB data make sure that the file is saved under the correct name
in its CSV form. Then go onto the "startTime" column in excel and format the column
as Time. The number should change to clock form. Resave as xlsx under the name in 
df_load()
"""


def represent_int(s):
    """
    Tests if the quantity being
    investigated is an integer
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def represent_str(s):
    """
     Tests if the quantity being
     investigated is a string
     """
    try:
        str(s)
        return True
    except ValueError:
        return False


def file_selection_set():
    """
    Determining if file is being run via exe.py or if run as a standalone
    """
    while True:
        try:
            exe.path
        except AttributeError:
            print('Using path defined in local file')
            file_selection = r'\LC_Counterparty_Analysis.xlsx'
            break
        else:
            file_selection = r'\LC_Ranking_Out.xlsx'
            break
    return file_selection


def df_load(file_selection, path):
    """
    Loads the file names to dataframes
    """

    df = Tier_Pull.read_xlsx_file(path + file_selection,
                                  "Performance")

    df_ranking = Tier_Pull.read_xlsx_file(path + file_selection,
                                          "Tier Ranking")

    df_tier_change = Tier_Pull.read_xlsx_file(path + file_selection,
                                              "Tier Changes")

    df_kdb_ALPHA = Tier_Pull.read_xlsx_file(path + "\KDB_TIER_INFO_ALPHA.xlsx",
                                            "KDB_TIER_INFO_ALPHA")

    df_kdb_MI = Tier_Pull.read_xlsx_file(path + "\KDB_TIER_INFO_MI.xlsx",
                                         "KDB_TIER_INFO_MI")

    return df, df_ranking, df_tier_change, df_kdb_ALPHA, df_kdb_MI


def df_quick_look_metrics(path):
    """
    Loads the file names to dataframes
    """

    df_added_removed = Tier_Pull.read_xlsx_file(path + "\LC_Counterparty_Analysis.xlsx",
                                                "Added_Removed")

    df_Metrics = Tier_Pull.read_xlsx_file(path + "LC_Counterparty_Analysis.xlsx",
                                          "Added_Removed")

    return df_added_removed, df_Metrics


def view_or_copy(df, df2):
    """
    Checks if dataframe is a copy or view
    of another dataframe. Useful for checking
    whether chain indexing issues will arrive
    Chained assignment warning was turned off
    in imports already
    """
    if df.values.base is df2.values.base:
        print('A view')
    else:
        print('A copy')


def nan_column(df, name):
    """
    Creates empty column with no assumed dtype
    """
    df[name] = ''
    return df


def excel_writer(ws_dict, df_analysis, df_analysis_2, df_LP_1, df_LP_2, df_LC_1, df_LC_2, path):
    """
    Writes the dataframe to a new file, should
    update this to append to existing file later
    """
    writer_location = path + "\LC_Counterparty_Analysis.xlsx"
    writer = pd.ExcelWriter(writer_location)
    for ws in ws_dict:
        df = ws_dict[ws]
        df.to_excel(writer, ws)

    df_analysis.to_excel(writer, sheet_name='Added_Removed', startcol=0, index=False)
    df_analysis_2.to_excel(writer, sheet_name='Added_Removed', startcol=7, index=False)
    df_LP_1.to_excel(writer, sheet_name='Metrics', startcol=0, index=False)
    df_LP_2.to_excel(writer, sheet_name='Metrics', startcol=7, index=False)
    df_LC_1.to_excel(writer, sheet_name='Metrics', startcol=0, startrow=10, index=False)
    df_LC_2.to_excel(writer, sheet_name='Metrics', startcol=7, startrow=10, index=False)
    writer.save()
    writer.close()
    return


def date_conversion(df):
    """
    Converts df to datetime object
    :param df:
    :return: datetime object
    """
    df['TIME'] = df['TIME'].str[0:21]
    df['TIME'] = pd.to_datetime(df.TIME, format='%Y-%m-%d %H:%M:%S.%f')
    df['TIME'] = df.TIME.dt.round('1s')
    return df


def date_order(df):
    """
    Orders the dataframe by date/time
    """
    df.sort_values(by='TIME', inplace=True)
    df = df.reset_index(drop=True)
    """
    Need to check that when added the drop=True condition that it hasnt resulted in the dates getting mixed up
    """
    return df


def first_and_last_date(df):
    ordered = df.sort_values(by='TIME')
    first_date = ordered['TIME'][0]
    last_date = ordered['TIME'][len(ordered) - 1]
    return first_date, last_date


def sweepable_assignment(df):
    """
    Assigns sweepable non-sweepable
    information to a dataframe column
    """
    LC_list = df['LC_ACCOUNT'].unique()

    sweep_index = df.columns.get_loc("Sweep")

    for LC in LC_list:

        filter_LC = df.loc[df['LC_ACCOUNT'] == LC]
        LP_list = filter_LC['LP Floor ID'].unique()

        for LP in LP_list:

            filter_LP = filter_LC.loc[df['LP Floor ID'] == LP]

            for index, row in filter_LP.iterrows():

                if represent_int(row['Tier Code']):
                    df.iat[index, sweep_index] = 'Single Ticket'
                elif represent_str(row['Tier Code']):
                    df.iat[index, sweep_index] = 'Sweepable'
    return df


def days_assignment(df, final_date):
    sweep_list = df['Sweep'].unique()

    for sweep in sweep_list:
        filter_sweep = df.loc[(df['Sweep'] == sweep)]
        LC_list = filter_sweep['LC_ACCOUNT'].unique()

        for LC in LC_list:

            filter_LC = filter_sweep.loc[filter_sweep['LC_ACCOUNT'] == LC]
            LP_list = filter_LC['LP Floor ID'].unique()

            for LP in LP_list:
                filter_LP = filter_LC.loc[filter_LC['LP Floor ID'] == LP]
                TC_list = filter_LP['Tier Code'].unique()

                for tier_code in TC_list:

                    filter_TC = filter_LP.loc[filter_LP['Tier Code'] == tier_code]
                    ordered_df = date_order(filter_TC)

                    for index, row in ordered_df.iterrows():

                        if index < (len(ordered_df) - 1) and (row['STATUS'] == 'Entitlement added' or
                                                              row['STATUS'] == 'Entitlement initialized'):
                            d0 = ordered_df.iloc[index]
                            d1 = ordered_df.iloc[index + 1]

                            if d1['STATUS'] == 'Entitlement removed':
                                delta = d1['TIME'] - d0['TIME']
                                df.loc[(df['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                                       (df['Sweep'] == row['Sweep']) &
                                       (df['STATUS'] == 'Entitlement added')
                                       & (df['TIME'] == row['TIME']), 'Duration'] = delta

                            elif d1['STATUS'] == 'Entitlement removed':
                                delta = d1['TIME'] - d0['TIME']
                                df.loc[(df['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                                       (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                                       (df['Sweep'] == row['Sweep']) &
                                       (df['STATUS'] == 'Entitlement initialized')
                                       & (df['TIME'] == row['TIME']), 'Duration'] = delta

                            elif d1['Tier Code'] != row['Tier Code']:
                                print('Double Add for', d0['LC_ACCOUNT'],
                                      'On LP Tier:', d0['LP_TIER'])

                        elif (index == len(ordered_df) - 1) and row['STATUS'] == 'Entitlement added':
                            d0 = ordered_df.iloc[index]
                            delta = final_date - d0['TIME']

                            df.loc[(df['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                                   (df['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                                   (df['Sweep'] == row['Sweep']) &
                                   (df['STATUS'] == 'Entitlement added') &
                                   (df['TIME'] == row['TIME']), 'Duration'] = delta
    return df


def days_initialized(df):
    sweep_list = df['Sweep'].unique()

    for sweep in sweep_list:
        filter_sweep = df.loc[(df['Sweep'] == sweep)]
        LC_list = filter_sweep['LC_ACCOUNT'].unique()

        for LC in LC_list:

            filter_LC = filter_sweep.loc[df['LC_ACCOUNT'] == LC]
            LP_list = filter_LC['LP Floor ID'].unique()

            for LP in LP_list:
                filter_LP = filter_LC.loc[filter_LC['LP Floor ID'] == LP]
                ordered_df = date_order(filter_LP)

                initial = ordered_df.loc[ordered_df['STATUS'] == 'Entitlement initialized']

                if not initial.empty:
                    df_removed = ordered_df.loc[ordered_df['STATUS'] == 'Entitlement removed']
                    first_removed = df_removed.iloc[0]
                    initial = initial.iloc[0]
                    delta = first_removed['TIME'] - initial['TIME']
                    df.loc[(df['LP_ACCOUNT'] == initial['LP_ACCOUNT']) &
                           (df['LC_ACCOUNT'] == initial['LC_ACCOUNT']) &
                           (df['Sweep'] == initial['Sweep']) &
                           (df['STATUS'] == 'Entitlement initialized')
                           & (df['TIME'] == initial['TIME']), 'Duration'] = delta

    return df


def ranking_add(df, df_ranking):
    for index, row in df.iterrows():
        tier_of_interest = df_ranking.loc[df_ranking['LP FloorCode'] == (row['LP_TIER'])]
        if not tier_of_interest['Ranking'].empty:
            rank = tier_of_interest['Ranking'].get_values()
            df.loc[(df['LP_TIER']) == (row['LP_TIER']), 'Ranking'] = rank
    return df


def large_and_small(df, LP_LC):
    LP_LC_list = df[LP_LC].unique()

    df_analysis = pd.DataFrame(LP_LC_list, columns=[LP_LC])

    for target in LP_LC_list:
        added = df.loc[(df[LP_LC] == target) &
                       (df["STATUS"] == 'Entitlement added')]
        removed = df.loc[(df[LP_LC] == target) &
                         (df["STATUS"] == 'Entitlement removed')]

        df_analysis.loc[(df_analysis[LP_LC] == target), 'Added'] = int(added.shape[0])
        df_analysis.loc[(df_analysis[LP_LC] == target), 'Removed'] = int(removed.shape[0])
        df_analysis.loc[(df_analysis[LP_LC] == target), 'Net'] = int((added.shape[0] - removed.shape[0]))

    largest = df_analysis.nlargest(5, columns=['Net'])
    smallest = df_analysis.nsmallest(5, columns=['Net'])

    return df_analysis, largest, smallest


def initial_tier_initilization(df, start_date):

    sweep_list = df['Sweep'].unique()
    status_list = df['STATUS'].unique()
    if 'Entitlement initialized' in status_list:
        print('Already ran Tier Pull')
    else:

        for sweep in sweep_list:
            filter_sweep = df.loc[(df['Sweep'] == sweep)]
            LC_list = filter_sweep['LC_ACCOUNT'].unique()

            for LC in LC_list:
                filter_LC = df.loc[df['LC_ACCOUNT'] == LC]
                LP_list = filter_LC['LP Floor ID'].unique()

                for LP in LP_list:
                    filter_LP = filter_LC.loc[(filter_LC['LP Floor ID'] == LP) &
                                              (filter_LC['STATUS'] == 'Entitlement removed') &
                                              (filter_LC['Sweep'] == sweep)]

                    if not filter_LP.empty:
                        df_reset = date_order(filter_LP)
                        row = (df_reset.iloc[0])
                        row['STATUS'] = 'Entitlement initialized'
                        row['DETAILS'] = 'Entitlement initialized'
                        row['TIME'] = start_date
                        df = df.append(row, ignore_index=True)

    return df


def time_and_date_priming_kdb(df):
    df['startDate'] = df['startDate'].str.replace('.', '-')
    df["TIME"] = df['startDate'] + ' ' + df["startTime"].astype(str).str[0:10]
    df['TIME'] = df['TIME'].str[0:21]
    df['TIME'] = pd.to_datetime(df.TIME, format='%Y-%m-%d %H:%M:%S.%f')
    df['TIME'] = df.TIME.dt.round('1s')
    return df


def currency_primer(df):
    df['CCY_PAIR'] = df['CCY_PAIR'].str.replace('/', '')
    df['CCY_PAIR'] = df['CCY_PAIR'].str[3:]
    return df


def row_of_interest(df_tier_change, df_kdb_ALPHA, df_kdb_MI):

    for index, row in df_tier_change.iterrows():

        target_row_ALPHA = df_kdb_ALPHA.loc[(df_kdb_ALPHA['TIME'] == row['TIME']) &
                                            (df_kdb_ALPHA['counterParty'] == row['LP_ACCOUNT']) &
                                            (df_kdb_ALPHA['floorCode'] == row['LC_ACCOUNT']) &
                                            (df_kdb_ALPHA['symList'] == row['CCY_PAIR'])]

        target_row_MI = df_kdb_MI.loc[(df_kdb_MI['TIME'] == row['TIME']) &
                                      (df_kdb_MI['counterParty'] == row['LP_ACCOUNT']) &
                                      (df_kdb_MI['floorCode'] == row['LC_ACCOUNT']) &
                                      (df_kdb_MI['symList'] == row['CCY_PAIR'])]


        '''
        Can use these rows for visualising what data is not in the dataframe
        Although for full run have these lines inactive otherwise causes
        issues later in program

        target_row_ALPHA = target_row_ALPHA.fillna('NA')
        target_row_MI = target_row_MI.fillna('NA')
        '''
        if not target_row_ALPHA.empty:
            VOL = target_row_ALPHA['baseDeals']
            VOL = VOL.iloc[0]
            df_tier_change.loc[(df_tier_change['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                               (df_tier_change['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df_tier_change['STATUS'] == 'Entitlement added') &
                               (df_tier_change['TIME'] == row['TIME']),
                               'Traded Vol (m)'] = VOL

        if not target_row_MI.empty:
            M2M = target_row_MI['PnLPm0']
            MI = target_row_MI['PnLPm30']
            M2M = M2M.iloc[0]
            MI = MI.iloc[0]

            df_tier_change.loc[(df_tier_change['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                               (df_tier_change['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df_tier_change['STATUS'] == 'Entitlement added') &
                               (df_tier_change['TIME'] == row['TIME']),
                               'MarkToMid 0s'] = M2M

            df_tier_change.loc[(df_tier_change['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                               (df_tier_change['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df_tier_change['STATUS'] == 'Entitlement added') &
                               (df_tier_change['TIME'] == row['TIME']),
                               'EBS Avg. MI 30s'] = MI

        if not target_row_ALPHA.empty:

            ALPHA = target_row_ALPHA['aMil']
            REJ =target_row_ALPHA['LPRej']
            ALPHA = ALPHA.iloc[0]
            REJ = REJ.iloc[0]

            df_tier_change.loc[(df_tier_change['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                               (df_tier_change['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df_tier_change['STATUS'] == 'Entitlement added') &
                               (df_tier_change['TIME'] == row['TIME']),
                               'Net Alpha (USD per mil)'] = ALPHA

            df_tier_change.loc[(df_tier_change['LP_ACCOUNT'] == row['LP_ACCOUNT']) &
                               (df_tier_change['LC_ACCOUNT'] == row['LC_ACCOUNT']) &
                               (df_tier_change['STATUS'] == 'Entitlement added') &
                               (df_tier_change['TIME'] == row['TIME']),
                               'LP Reject %'] = REJ

    return df_tier_change


def main():
    start_time_TA = time.clock()

    file_selection = file_selection_set()
    path = Tier_Pull.path_set()

    df_performance, df_ranking, df_tier_change, df_kdb_ALPHA, df_kdb_MI = df_load(file_selection, path)

    if 'Out' in file_selection:
        print('Running Out File')
        df_tier_change = nan_column(df_tier_change, 'Sweep')

        df_tier_change = date_conversion(df_tier_change)

        start_date, final_date = first_and_last_date(df_tier_change)

        print(start_date)

        df_tier_change = sweepable_assignment(df_tier_change)

        df_tier_change = initial_tier_initilization(df_tier_change, start_date)

        df_tier_change = days_assignment(df_tier_change, final_date)

        df_tier_change = days_initialized(df_tier_change)

        df_tier_change = ranking_add(df_tier_change, df_ranking)

        df_tier_change = currency_primer(df_tier_change)

    df_analysis, largest_LP, smallest_LP = large_and_small(df_tier_change, 'LP_ACCOUNT')

    df_analysis_2, largest_LC, smallest_LC = large_and_small(df_tier_change, 'LC_ACCOUNT')

    '''
    For process of matching up KDB database and LPM data the information in the data
    and time column has been reduced. The lowest granularity is seconds, if morye
    granulatity is needed would need to create additional dataframe sheet but seems
    unnecessary for now'''

    df_kdb_ALPHA = time_and_date_priming_kdb(df_kdb_ALPHA)
    df_kdb_MI = time_and_date_priming_kdb(df_kdb_MI)

    df_tier_change = row_of_interest(df_tier_change, df_kdb_ALPHA, df_kdb_MI)

    df_dict = {'Performance': df_performance,
               'Tier Ranking': df_ranking,
               'Tier Changes': df_tier_change}

    excel_writer(df_dict, df_analysis, df_analysis_2, largest_LP, smallest_LP, largest_LC, smallest_LC, path)

    print('Tier Analysis,', time.clock() - start_time_TA, "seconds")


if __name__ == '__main__':
    main()
