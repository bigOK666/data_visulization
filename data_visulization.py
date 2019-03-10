import pandas as pd

df = pd.read_csv('Topic_Survey_Assignment.csv', index_col=0)

print(df.head())

#sort values based on "very interested" in decending method

df.sort_values(by='Very interested', ascending=False)