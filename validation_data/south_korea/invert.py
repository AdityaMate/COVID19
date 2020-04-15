import numpy as np
import pandas as pd 

df = pd.read_csv('south_korea_inverted.csv',header=None)
print(df)
vals = df.values
vals = vals.T

print(vals)
df = pd.DataFrame(vals[1:],columns=vals[0])
print(df)

df.to_csv('south_korea.csv',index=False)