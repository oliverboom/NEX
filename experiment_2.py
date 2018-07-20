import pandas as pd
import Tier_Analysis
df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})


print(df.values.base)

df2 = df.copy()
Tier_Analysis.view_or_copy(df,df)