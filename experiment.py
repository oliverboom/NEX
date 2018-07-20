import pandas as pd
import numpy as np
import math
import Tier_Pull
import exe
import Tier_Analysis



path = r"\\newco.global\newcoroot\Global\EMEA\userdir$\o_boom\Oliver"
file_selection = r'\LC_Counterparty_Analysis.xlsx'

df_tier_change = Tier_Pull.read_xlsx_file(path + "\LC_Counterparty_Analysis.xlsx",
                                          "Tier Changes")

df_kdb_ALPHA = Tier_Pull.read_xlsx_file(path + "\KDB_TIER_INFO_ALPHA.xlsx",
                                        "KDB_TIER_INFO_ALPHA")

df_kdb_MI = Tier_Pull.read_xlsx_file(path + "\KDB_TIER_INFO_MI.xlsx",
                                     "KDB_TIER_INFO_MI")

df_kdb_ALPHA = Tier_Analysis.time_and_date_priming_kdb(df_kdb_ALPHA)
df_tier_change = df_tier_change.loc[df_tier_change['STATUS'] == 'Entitlement initialized']

print(type(df_kdb_ALPHA['TIME'].iloc[0]))
for index, row in df_tier_change.iterrows():
  print(type(row['TIME']))
  print(type(df_kdb_ALPHA['TIME'][0]))


  target_row_ALPHA = df_kdb_ALPHA.loc[(df_kdb_ALPHA['TIME'] == row['TIME']) &
                                    (df_kdb_ALPHA['counterParty'] == row['LP_ACCOUNT']) &
                                    (df_kdb_ALPHA['floorCode'] == row['LC_ACCOUNT']) &
                                    (df_kdb_ALPHA['symList'] == row['CCY_PAIR'])]
  if not target_row_ALPHA.empty:
    print(target_row_ALPHA)