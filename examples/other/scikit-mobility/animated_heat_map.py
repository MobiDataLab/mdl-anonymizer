from datetime import timedelta

import folium
#import imageio
import numpy as np
import skmob
from folium.plugins import HeatMapWithTime
from skmob.utils import plot, constants

# def create_maps(tdf, lapse = 600):
#
#     min_ts = tdf['datetime'].min()
#     max_ts = tdf['datetime'].max()
#
#     from_ts = min_ts
#     to_ts = from_ts + timedelta(seconds=lapse)
#
#     while from_ts < max_ts:
#
#         mask = (tdf['datetime'] >= from_ts) & (tdf['datetime'] < to_ts)
#
#         heatmap = plot.plot_points_heatmap(tdf[mask], zoom=12, tiles='Stamen Toner', zoom_control=False)
#         heatmap.save(f'maps/animated/heatmap_{from_ts.timestamp()}_{to_ts.timestamp()}.html')
#
#         from_ts = to_ts
#         to_ts = from_ts + timedelta(seconds=lapse)


tdf = skmob.TrajDataFrame.from_file('../anonymize/out/actual_dataset_loaded.csv', latitude='lat', longitude='lon', datetime='timestamp', user_id='user_id')


# create_maps(tdf)

# Anonymized
# tdf = skmob.TrajDataFrame.from_file('dataset/cabs_scikit_anonymized.csv', latitude='lat', longitude='lon', datetime='timestamp', user_id='user_id')

def plot_points_heatmap_with_time(tdf, map_f=None, lapse=600, max_points=1000,
                        tiles='cartodbpositron', zoom=2,
                        min_opacity=0.5, radius=25,
                        gradient=None):

    #tdf.sort_values(by=constants.DATETIME, inplace=True)

    # locations = tdf[[constants.LATITUDE, constants.LONGITUDE]]
    #time_index = tdf[[constants.DATETIME]]

    locations = []

    min_ts = tdf['datetime'].min()
    max_ts = tdf['datetime'].max()

    from_ts = min_ts
    to_ts = from_ts + timedelta(seconds=lapse)

    while from_ts < max_ts:

        mask = (tdf['datetime'] >= from_ts) & (tdf['datetime'] < to_ts)

        locations.append(tdf[mask][[constants.LATITUDE, constants.LONGITUDE]].values.tolist())

        from_ts = to_ts
        to_ts = from_ts + timedelta(seconds=lapse)

    if map_f is None:
        center = list(np.median(tdf[[constants.LATITUDE, constants.LONGITUDE]], axis=0)[::-1])
        print(center)
        map_f = folium.Map(zoom_start=zoom, tiles=tiles, control_scale=True, location=center)


    HeatMapWithTime(locations,
            min_opacity=min_opacity, radius=radius,
            gradient=gradient).add_to(map_f)

    return map_f


heatmaptime = plot_points_heatmap_with_time(tdf, zoom=6)
heatmaptime.save('maps/heatmap_orig_time.html')