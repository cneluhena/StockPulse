# In a local Python/Jupyter notebook
import pandas as pd

# Read parquet files
df = pd.read_parquet('./data/')
df.to_json('output.json', orient='records', indent=2)
print(df)