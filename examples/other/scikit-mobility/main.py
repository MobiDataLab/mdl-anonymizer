import skmob
from folium import folium
from folium.plugins import HeatMap
from skmob.measures.individual import radius_of_gyration, home_location
from skmob.utils import plot
import numpy as np

tdf = skmob.TrajDataFrame.from_file('../anonymize/output/actual_dataset_loaded.csv', latitude='lat', longitude='lon', datetime='timestamp', user_id='user_id')

# First trajectories
n_users = 20
nth_user_id = np.sort(np.unique(tdf['uid']))[n_users]
first_traj = tdf[tdf['uid'] <= nth_user_id]

m = first_traj.plot_trajectory(max_users=n_users, zoom=12, weight=3, opacity=0.9, tiles='Stamen Toner')
m.save('maps/map_orig.html')

#HeatMap(tdf[['lat', 'lng']].values).add_to(m)
heatmap = plot.plot_points_heatmap(tdf, zoom=12, tiles='Stamen Toner')
heatmap.save('maps/heatmap_orig.html')

# rg_df = radius_of_gyration(tdf)
# print(rg_df)
# hl_df = home_location(tdf)
# print(hl_df.head())



tdf = skmob.TrajDataFrame.from_file('../anonymize/output/cabs_scikit_anonymized.csv', latitude='lat', longitude='lon', datetime='timestamp', user_id='user_id')

# First usaers
nth_user_id = np.sort(np.unique(tdf['uid']))[n_users]
first_traj = tdf[tdf['uid'] <= nth_user_id]

m = first_traj.plot_trajectory(zoom=12, weight=3, opacity=0.9, tiles='Stamen Toner')
m.save('maps/map_anon.html')

#HeatMap(tdf[['lat', 'lng']].values).add_to(m)
heatmap = plot.plot_points_heatmap(tdf, zoom=12, tiles='Stamen Toner')
heatmap.save('maps/heatmap_anon.html')

