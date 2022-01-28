import skmob
from folium import folium
from folium.plugins import HeatMap
from skmob.measures.individual import radius_of_gyration, home_location
from skmob.utils import plot

tdf = skmob.TrajDataFrame.from_file('dataset/actual_dataset_loaded.csv', latitude='lat', longitude='lon', datetime='timestamp', user_id='user_id')
#first trajectories
first_traj = tdf[tdf['uid'] < 20]

m = first_traj.plot_trajectory(zoom=12, weight=3, opacity=0.9, tiles='Stamen Toner')
m.save('maps/map_orig.html')

#HeatMap(tdf[['lat', 'lng']].values).add_to(m)
heatmap = plot.plot_points_heatmap(tdf, zoom=12, tiles='Stamen Toner')
heatmap.save('maps/heatmap_orig.html')

# rg_df = radius_of_gyration(tdf)
# print(rg_df)
# hl_df = home_location(tdf)
# print(hl_df.head())



tdf = skmob.TrajDataFrame.from_file('dataset/cabs_scikit_anonymized.csv', latitude='lat', longitude='lon', datetime='timestamp', user_id='user_id')

first_traj = tdf[tdf['uid'] < 20]

m = first_traj.plot_trajectory(zoom=12, weight=3, opacity=0.9, tiles='Stamen Toner')
m.save('maps/map_anon.html')

#HeatMap(tdf[['lat', 'lng']].values).add_to(m)
heatmap = plot.plot_points_heatmap(tdf, zoom=12, tiles='Stamen Toner')
heatmap.save('maps/heatmap_anon.html')

