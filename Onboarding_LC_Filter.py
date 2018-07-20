import pandas as pd
import time

'''
Function to pull out the relevant LC Floor Code
to be saved into an excel file for later 
manipulation in Python pandas framework
Interpreter: 3.6.5 |Anaconda, Inc
'''

# def LC_filter(LC_code, start_date, end_date, start_year, end_year):

LC_code = 'TUDZ'
start_date = 'January'
start_year = '2017'
end_date = 'June'
end_year = '2017'
start_time = time.clock()

base_location = (r"\\newco.global\NewCoRoot\Global\EMEA"
                 r"\Department\Electronic Broking\Brokertec"
                 r"\EBS Direct\Liquidity Management\MONTHLY DATA")

month_list = ['January', 'February', 'March',
              'April', 'May', 'June', 'July',
              'August', 'September', 'October',
              'November', 'December']
year_list = ['2017', '2018', '2019', '2020']

start_date_index = month_list.index(start_date)
end_date_index = month_list.index(end_date)
start_year_index = year_list.index(start_year)
end_year_index = year_list.index(end_year)
year_slice = year_list[start_year_index:end_year_index + 1]

a = 0

'''
Creating wraparound to iterate through
the designated time being investigated
'''

for x in range(start_year_index, end_year_index + 1):

    if len(year_slice) > 1:

        if x == start_year_index:
            month_selection = month_list[start_date_index:12]

        elif x == end_year_index:
            month_selection = month_list[0:end_date_index + 1]

        else:
            month_selection = month_list

    elif len(year_slice) == 1 and start_date_index != end_date_index:
        month_selection = month_list[start_date_index:end_date_index]

    elif len(year_slice) == 1 and start_date_index == end_date_index:
        month_selection = month_list[start_date_index:(start_date_index + 1)]

    for elements in month_selection:
        a += 1
        print(elements, year_list[x])
        file_location = base_location + '\\' + year_list[x] + '\\' + elements
        file_inspection = r"\Monthly " + elements + ' ' + year_list[x] + ".xlsx"
        path = r"\\newco.global\newcoroot\Global\EMEA\userdir$\o_boom\Oliver"
        df = pd.read_excel(file_location + file_inspection, sheet_name='Data')

        df_filter = df[df['LC_FLOOR_CODE'].str.contains(LC_code)]
        df_filter = df_filter.reset_index(drop=True)

        df_filter = df_filter[["HIT_TIME", "LC_ORDER_ID", "LC_REGION", "LC_FLOOR_CODE",
                               "LC_TRADER_ID", "EXECUTION_ID", "LP_FLOOR_CODE",
                               "CCY_PAIR_SHORT_ISO", "HIT_AMONUT", "HIT_PRICE",
                               "NOS_AMONUT", "NOS_PRICE", "DEAL_AMOUNT", "DEALT_PRICE",
                               "REJECT_REASON", "ORDER_STATUS", "LP_DEAL_ID",
                               "SLP", "ATTR", "SIDE", "IS_MANUAL_ORDER"]]

        print(elements, year_list[x], 'Number of Transactions by', LC_code, ':', len(df_filter.index))

        if a == 1:
            df_filter.to_csv(path + '\\' + LC_code + start_date + '_' +
                             end_date + '_Investigation.csv', mode='w', index=False)
        else:
            df_filter.to_csv(path + '\\' + LC_code + start_date + '_' +
                             end_date + '_Investigation.csv', mode='a', index=False, header=False)

print(time.clock() - start_time, "seconds")

# LC_filter('120Y', 'February', 'March', '2017', '2017')
