import pandas as pd

df = pd.read_csv('nasdaq100.csv', header=0, names=['value', 'label'])
df[['label', 'value']].to_dict('records')