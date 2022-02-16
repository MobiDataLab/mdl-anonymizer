import skmob
from skmob.measures.individual import radius_of_gyration, jump_lengths, home_location

tdf = skmob.TrajDataFrame.from_file('../anonymize/out/actual_dataset_loaded.csv', latitude='lat', longitude='lon', datetime='timestamp', user_id='user_id')


anon_tdf = skmob.TrajDataFrame.from_file('../anonymize/out/cabs_scikit_anonymized.csv', latitude='lat', longitude='lon', datetime='timestamp', user_id='user_id')


# Radius of Gyration
rg_df = radius_of_gyration(tdf)
print(rg_df)
anon_rg_df = radius_of_gyration(anon_tdf)
print(anon_rg_df)


# Jump Lengths
jl_df = jump_lengths(tdf.sort_values(by='datetime'))
print(jl_df.head())

anon_jl_df = jump_lengths(anon_tdf.sort_values(by='datetime'))
print(anon_jl_df.head())

# Home location
hl_df = home_location(tdf)
print(hl_df.head())
anon_hl_df = home_location(anon_tdf)
print(anon_hl_df.head())