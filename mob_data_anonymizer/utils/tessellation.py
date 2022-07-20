import pandas as pd
from shapely import geometry
from geopandas import GeoDataFrame
import skmob
from skmob import TrajDataFrame
from skmob.tessellation import tilers
from skmob.utils.constants import DEFAULT_CRS


def _get_bounding_box(tdf):
    # Build bounding box for tesselation
    # Get max, min lat
    max_lat = tdf['lat'].max()
    min_lat = tdf['lat'].min()

    # Get max, min lng
    max_lng = tdf['lng'].max()
    min_lng = tdf['lng'].min()

    point_list = [[max_lng, max_lat], [max_lng, min_lat], [min_lng, min_lat], [min_lng, max_lat]]

    poly = geometry.Polygon(point_list)
    polygon = GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[poly])

    return polygon


def tessellate(tdf: TrajDataFrame, tiles_shape, meters=250, bounding_box=None) -> TrajDataFrame:
    # tdf = skmob.TrajDataFrame.from_file('dataset/actual_dataset_loaded.csv', latitude='lat', longitude='lon',
    #                                    datetime='timestamp', user_id='user_id')

    # Compute bounding_box
    if bounding_box is None:
        bounding_box = _get_bounding_box(tdf)

    # Build tiles
    tessellation = tilers.tiler.get(tiles_shape, base_shape=bounding_box, meters=meters)

    # Map locations to tiles
    mtdf = tdf.mapping(tessellation, remove_na=True)

    # Add centroid locations of every tile to dataframe
    centroids = pd.DataFrame({
    })

    centroids['tile_ID'] = tessellation['tile_ID']
    centroids['x'] = round(tessellation['geometry'].centroid.x, 5)
    centroids['y'] = round(tessellation['geometry'].centroid.y, 5)

    # Merge with Mapped locations
    new_tdf = pd.merge(mtdf, centroids, how='left', on='tile_ID')

    # Rename and reorder columns
    new_tdf.rename(columns={
        'lat': 'orig_lat',
        'lng': 'orig_lng',
        'x': 'lng',
        'y': 'lat',
    }, inplace=True)
    new_tdf = new_tdf[['lng', 'lat', 'datetime', 'uid', 'tile_ID', 'orig_lng', 'orig_lat']]

    return new_tdf
