import pandas as pd
import pyarrow.parquet as pq

INPUT_FILE = "../examples/output/f_CNR_Rome.parquet"
output_file = INPUT_FILE[:-7] + "csv"

df = pq.read_table(INPUT_FILE).to_pandas()
df.to_csv(output_file)