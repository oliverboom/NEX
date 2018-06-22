import pandas as pd
import time

start_time = time.clock()

base_location = (r"\\newco.global\NewCoRoot\Global\EMEA"
                 r"\Department\Electronic Broking\Brokertec"
                 r"\EBS Direct\Liquidity Management\MONTHLY DATA\2017")


'''Search Criteria'''
LC_code = '120Y'
start_date = 'November'
start_year = '2017'
end_date = 'February'
end_year = '2018'

month_list = ['January', 'February', 'March',
              'April', 'May', 'June', 'July',
              'August', 'September', 'October',
              'November', 'December']
year_list = ['2017', '2018']

start_date_index = month_list.index(start_date)
end_date_index = month_list.index(end_date)
start_year_index = year_list.index(start_year)
end_year_index = year_list.index(end_year)

if start_year == end_year:
    month_selection = month_list[start_date_index:end_date_index]
    year_selection = [start_year]
else:
    month_selection_0 = month_list[start_date_index:12]
    month_selection_1 = month_list[0:end_date_index+1]
    year_list = year_list[start_year_index:end_year_index+1]

a = 0

for items in year_list:
    print(items)
    foo = 'month_selection_' + str(year_list.index(items))

    '''The issue is having
    a string pointing at a variable
    Look up dynamically set local 
    variables on return
    '''

    for elements in foo:
        a += 1
        print(elements, items)

        # file_location = base_location + '\\' + elements
        # file_inspection = '\Monthly ' + elements + ' ' + items + '.xlsx'
        # path = r"\\newco.global\newcoroot\Global\EMEA\userdir$\o_boom\Oliver"
        #
        # df = pd.read_excel(file_location + file_inspection, sheet_name='Data')
        #
        # df_filter = df[df['LC_FLOOR_CODE'].str.contains(LC_code)]
        # df_filter = df_filter.reset_index(drop=True)
        # print(len(df_filter.index))
        #
        # if a == 1:
        #     df_filter.to_csv(path + '\\' + LC_code + '_investigation.csv', mode='w', index=False)
        # else:
        #     df_filter.to_csv(path + '\\' + LC_code + '_investigation.csv', mode='a', index=False, header=False)

print(time.clock() - start_time, "seconds")