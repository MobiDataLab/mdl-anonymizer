import pandas as pd
from shapely import geometry
from geopandas import GeoDataFrame
import skmob
from skmob import TrajDataFrame
from skmob.tessellation import tilers
from skmob.utils import constants
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


def spatial_tessellation(tdf: TrajDataFrame, tiles_shape, meters=250, tiles=None, bounding_box=None) -> TrajDataFrame:
    '''

    :param tdf: tdf to be tessellated
    :param tiles_shape:
    :param meters: size of the tiles
    :param tiles: If a tiles file is provided is used, if not the are computed
    :param bounding_box: If a bounding_box is not provided, it is computed
    :return: tuple of tdf mapped to tiles and tiles computed
    '''

    # Build tiles
    if tiles is None:
        if bounding_box is None:
            # Compute bounding_box
            bounding_box = _get_bounding_box(tdf)

        tiles = tilers.tiler.get(tiles_shape, base_shape=bounding_box, meters=meters)

    # Map locations to tiles
    mtdf = tdf.mapping(tiles, remove_na=True)

    return mtdf, tiles


def generalization(tdf: TrajDataFrame, size=250) -> TrajDataFrame:
    '''

    :param tdf: trajDataFrame to generalize
    :param size: size tile (meters)
    :return: TrajDataFrame with new positions generalized to the centroid of the corresponding tile. Also the tile_ID ç
    and the original position are included
    '''

    mtdf = spatial_tessellation(tdf, "squared", size)

    # Add centroid locations of every tile to dataframe
    centroids = pd.DataFrame({
    })

    mtdf['x'] = round(mtdf['geometry'].centroid.x, 5)
    mtdf['y'] = round(mtdf['geometry'].centroid.y, 5)

    # Rename and reorder columns
    mtdf.rename(columns={
        constants.LATITUDE: 'orig_lat',
        constants.LONGITUDE: 'orig_lng',
        'x': constants.LONGITUDE,
        'y': constants.LATITUDE,
    }, inplace=True)

    mtdf = mtdf[
        [constants.LONGITUDE, constants.LATITUDE, constants.DATETIME, constants.UID, constants.TID, 'tile_ID',
         'orig_lon', 'orig_lat']]

    return mtdf
