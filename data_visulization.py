import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('Topic_Survey_Assignment.csv', index_col=0)

print(df.head())

#sort values based on "very interested" in decending method

df_decend = df.sort_values(by='Very interested', ascending=False)

# use percentage format by dividing sum 2233
survey_sum = 2233

df_decend.loc[:, 'Very interested':'Not interested'] = df_decend.loc[:, 'Very interested':'Not interested'].div(survey_sum, axis=0).round(4).mul(100, axis=0)
# draw the bar charts
fig, ax = plt.subplots(figsize=(20,8))
bar_width=0.8
color_very_interested='#5cb85c'
color_somewhat_interested='#5bc0de'
color_not_interested='#d9534f'
df_decend.plot(kind='bar',ax = ax, title="Percentage of Respondents' Interest in Data Science Areas", color=[color_very_interested, color_somewhat_interested, color_not_interested], width=bar_width, fontsize=14)
ax.title.set_size(16)
plt.legend(fontsize=14)
# remove the left top right borders and axis ticks
plt.yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
