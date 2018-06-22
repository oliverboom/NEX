import pandas as pd
import time

'''
Function to pull out the relevant LC Floor Code
to be saved into an excel file for later 
manipulation in Python pandas framework
'''

def LC_filter(LC_code,start_date, end_date, start_year, end_year):

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
    year_slice = year_list[start_year_index:end_year_index+1]

    a = 0

    for x in range(start_year_index, end_year_index+1):

        if len(year_slice) > 1:

            if x == start_year_index:
                month_selection = month_list[start_date_index:12]

            elif x == end_year_index:
                month_selection = month_list[0:end_date_index + 1]

            else:
                month_selection = month_list

        elif len(year_slice) == 1:
            month_selection = month_list[start_date_index:end_date_index]

        for elements in month_selection:
            a += 1

            file_location = base_location + '\\' + year_list[x] + '\\' + elements
            file_inspection = r"\Monthly " + elements + ' ' + year_list[x] + ".xlsx"
            path = r"\\newco.global\newcoroot\Global\EMEA\userdir$\o_boom\Oliver"
            df = pd.read_excel(file_location + file_inspection, sheet_name='Data')

            df_filter = df[df['LC_FLOOR_CODE'].str.contains(LC_code)]
            df_filter = df_filter.reset_index(drop=True)

            print(elements, year_list[x], 'Number of Transactions by', LC_code, ':', len(df_filter.index))

            if a == 1:
                df_filter.to_csv(path + '\\' + LC_code + '_investigation.csv', mode='w', index=False)
            else:
                df_filter.to_csv(path + '\\' + LC_code + '_investigation.csv', mode='a', index=False, header=False)

    print(time.clock() - start_time, "seconds")


LC_filter('120Y', 'February', 'March', '2017', '2018')
