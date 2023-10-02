import pandas as pd

data = pd.read_excel('fall_schedule.xlsx')
column_headers = list(data.columns)

# number of rows: len(df)
# number of columns: len(df.columns)
# number of elements: df.size

x = data[data[column_headers[4]] == 'SYSC']
#.iloc[1]
print(x)
