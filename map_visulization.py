import pandas as pd


# read data from csv file
df = pd.read_csv('Police_Department_Incidents_-_Previous_Year__2016_.csv', index_col=0)

df_criminal = df.drop(df[(df.Category=="NON-CRIMINAL") | (df.Category=="MISSING PERSON") | (df.Category=="SUICIDE")].index)

ds_district=df_criminal["PdDistrict"].value_counts()

df_district=pd.DataFrame({'Neighborhood':ds_district.index, 'Count':ds_district.values})