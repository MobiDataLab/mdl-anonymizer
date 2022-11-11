import pandas as pd

INPUT_FILE = "../examples/out/cabs_dataset_20080608_0700_0730_uid.csv"
output_file = INPUT_FILE[:-3] + "parquet"

df = pd.read_csv(INPUT_FILE)
df.to_parquet(output_file)