import pandas as pd
import time
import csv

start_time = time.clock()



file_location = (r'\\newco.global\NewCoRoot\Global\EMEA\Department\Electronic Broking'
                r'\Brokertec\EBS Direct\Liquidity Management\MONTHLY DATA\2018\May 2018\MAY1.txt')


df = pd.read_csv(file_location, sep='"([^"]*)"', delim_whitespace=False, header=0, engine='python')

cols = df.columns.tolist()

df = df[['HIT_TIME', 'LC_ORDER_ID', 'EMS', 'LC_REGION', 'LC_FLOOR_CODE', 'LC_TRADER_ID',
         'EXECUTION_ID', 'LP_FLOOR_CODE', 'CCY_PAIR_SHORT_ISO', 'HIT_AMONUT',
         'HIT_PRICE', 'NOS_AMONUT',  'NOS_PRICE', 'DEAL_AMOUNT', 'DEALT_PRICE',
         'REJECT_REASON', 'ORDER_STATUS', 'LP_DEAL_ID', 'SLP', 'ATTR', 'SIDE', 'IS_MANUAL_ORDER']]

LC_code = '120Y'

a = df[df['LC_FLOOR_CODE'].str.contains(LC_code)]
a = a.reset_index(drop=True)
print(len(a.index))


# path = r"\\newco.global\newcoroot\Global\EMEA\userdir$\o_boom\Oliver"
# a.to_csv(path + '\\' + LC_code + '_investigation.csv', mode='w', index=False, header=False)
#
# print(time.clock() - start_time, "seconds")
