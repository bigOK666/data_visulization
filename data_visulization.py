import pandas as pd

df = pd.read_csv('Topic_Survey_Assignment.csv', index_col=0)

print(df.head())

#sort values based on "very interested" in decending method

df_decend = df.sort_values(by='Very interested', ascending=False)

# use percentage format by dividing sum 2233
survey_sum = 2233

df_decend.loc[:, 'Very interested':'Not interested'] = df_decend.loc[:, 'Very interested':'Not interested'].div(survey_sum, axis=0).round(4).mul(100, axis=0)
