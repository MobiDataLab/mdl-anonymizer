import pandas as pd

INPUT_FILE = "Rome_taxi_dataset_to_CSV/rome_taxi_dataset_all.csv"
output_file = INPUT_FILE[:-3] + "parquet"

df = pd.read_csv(INPUT_FILE)
df.to_parquet(output_file)