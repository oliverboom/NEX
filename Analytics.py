import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt


'''
Analysis on singular LC floor code
Interpreter: 3.6.5 |Anaconda, Inc
'''

start_time = time.clock()

''' Specify the information being 
investigated and read in the file
'''

LC_code = 'TUDZ'
start_date = 'January'
start_year = '2017'
end_date = 'June'
end_year = '2017'

path = r"\\newco.global\newcoroot\Global\EMEA\userdir$\o_boom\Oliver"
file_location = (path + '\\' + LC_code + start_date + '_' + end_date + '_Investigation.csv')
df = pd.read_csv(file_location, engine='python', error_bad_lines=False)

# Splitting the hit time into separate columns

df['Date'] = df.HIT_TIME.str.split(' ').str.get(0)
df['Time'] = df.HIT_TIME.str.split(' ').str.get(1)
df.drop(['HIT_TIME'], axis=1, inplace=True)
cols = list(df)
cols.insert(0, cols.pop(cols.index('Date')))
cols.insert(1, cols.pop(cols.index('Time')))
df = df.ix[:, cols]

# Taking out key information

volume_traded = np.sum(df["DEAL_AMOUNT"])
pairs_traded = df["CCY_PAIR_SHORT_ISO"].value_counts()
traders = df["LC_TRADER_ID"].value_counts()
region = df["LC_REGION"].value_counts()
rejection_reason = df["REJECT_REASON"].value_counts()
order_count = df["ORDER_STATUS"].value_counts()
filled_count = order_count["eFilled"]
average_order_size = volume_traded / filled_count
days_traded_on = df["Date"].value_counts()
dealt_breakdown = df["DEAL_AMOUNT"].value_counts()
order_breakdown = df["HIT_AMONUT"].value_counts()
FA_vs_VWAP = df["ATTR"].value_counts()
trading_times = df['Time'].str[0:2].value_counts()

# Outputting results

d = pd.DataFrame({'Pairs Traded': pairs_traded})
d1 = pd.DataFrame({'Order Status': order_count})
d2 = pd.DataFrame({'LC Region': region})
d3 = pd.DataFrame({'Volume Traded': [volume_traded]})
d4 = pd.DataFrame({'Average order size:': [average_order_size]})
d5 = pd.DataFrame({'Days traded on:': days_traded_on.sort_index(ascending=True)})
d6 = pd.DataFrame({'Trader:': traders})
d7 = pd.DataFrame({'Reject Reason': rejection_reason})
d8 = pd.DataFrame({'Trading Timings': trading_times.sort_index(ascending=True)})
d9 = pd.DataFrame({'Order Amount': order_breakdown}).sort_index(ascending=True)
d10 = pd.DataFrame({'Dealt Amount': dealt_breakdown.sort_index(ascending=True)})
d11 = df.groupby(['CCY_PAIR_SHORT_ISO']).agg({'DEAL_AMOUNT': np.sum})
d12 = pd.DataFrame({'FA vs VWAP': FA_vs_VWAP})

writer = pd.ExcelWriter((path + '\\' + LC_code + '_' + start_date + '_' + end_date + '_Analysis.xlsx'))

d.to_excel(writer, 'Sheet1', startcol=0)
d1.to_excel(writer, 'Sheet1', startcol=3)
d2.to_excel(writer, 'Sheet1', startcol=6)
d3.to_excel(writer, 'Sheet1', startcol=9, index=None)
d4.to_excel(writer, 'Sheet1', startcol=11, index=None)
d5.to_excel(writer, 'Sheet1', startcol=13)
d6.to_excel(writer, 'Sheet1', startcol=16)
d7.to_excel(writer, 'Sheet1', startcol=19)
d8.to_excel(writer, 'Sheet1', startcol=22)
d9.to_excel(writer, 'Sheet1', startcol=25)
d10.to_excel(writer, 'Sheet1', startcol=28)
d11.to_excel(writer, 'Sheet1', startcol=32)
d12.to_excel(writer, 'Sheet1', startcol=35)

writer.save()

# pivot = pd.pivot_table(df,index=["DEAL_AMOUNT"], aggfunc=np.sum)
'''
df.plot(kind='box', subplots=True, layout=(3,3), sharex=False, sharey=False)
plt.show()

df.hist()
plt.show()
'''


print(time.clock() - start_time, "seconds")


