import warnings

import pandas as pd
from shapely import geometry
import geopandas as gpd
import skmob
from shapely.geometry import MultiPolygon, Polygon
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
    polygon = gpd.GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[poly])

    return polygon


def _tdf_to_geodataframe(tdf: TrajDataFrame):
    return gpd.GeoDataFrame(tdf.copy(), geometry=gpd.points_from_xy(tdf[constants.LONGITUDE],
                                                                    tdf[constants.LATITUDE]), crs=tdf._crs)


def _mapping(tdf: TrajDataFrame, tiles: gpd.GeoDataFrame, remove_na=True):
    # Check CSR
    if tiles.crs != tdf.crs:
        warnings.warn(f"CRS are different! Mapping may not be correct. \nData: {tdf.crs}\nTiles: {tiles.crs}")

    # Check all geometries are Polygon or MultiPolygon
    if any(not (isinstance(x, Polygon) or isinstance(x, MultiPolygon)) for x in tiles.geometry):
        warnings.warn(f"All geometries in 'tiles' should be Polygon or MultiPolygon")

    gdf = _tdf_to_geodataframe(tdf)

    if remove_na:
        how = 'inner'
    else:
        how = 'left'

    tile_ids = gpd.sjoin(gdf, tiles, how=how, predicate='within')[[constants.TILE_ID]]

    new_data = tdf.copy()
    new_data = new_data.merge(tile_ids, right_index=True, left_index=True)

    return new_data


def load_tiles_file(tiles_filename) -> gpd.GeoDataFrame:
    tiles = gpd.read_file(tiles_filename)
    tiles[constants.TILE_ID] = range(1, len(tiles) + 1)

    return tiles


def compute_centroids(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:

    tiles_3857 = gdf.to_crs('EPSG:3857')

    # tiles['x'] = round(tiles['geometry'].centroid.x, 5)
    # tiles['y'] = round(tiles['geometry'].centroid.y, 5)

    centroids = gpd.GeoDataFrame(geometry=gpd.points_from_xy(tiles_3857['geometry'].centroid.x,
                                                             tiles_3857['geometry'].centroid.y), crs="EPSG:3857")

    centroids = centroids.to_crs(gdf.crs)

    centroids['centroid_lon'] = centroids['geometry'].x
    centroids['centroid_lat'] = centroids['geometry'].y
    centroids = centroids.drop(['geometry'], axis=1)

    tiles = pd.merge(gdf, centroids, left_index=True, right_index=True)

    return tiles


def spatial_tessellation(tdf: TrajDataFrame, tiles: gpd.GeoDataFrame = None,
                         bounding_box=None, tiles_shape: str = "squared", meters: int = 250) \
        -> tuple:
    """

    :param tdf: tdf to be tessellated
    :param tiles_shape:
    :param meters: size of the tiles
    :param tiles: If a tiles GeoDataFrame is provided is used, if not tiles are generated
    :param bounding_box: If a bounding_box is not provided, it is computed for generating tiles

    :return: tuple of tdf mapped to tiles and tiles used
    """

    # Build tiles
    if tiles is None:
        if bounding_box is None:
            # Compute bounding_box
            bounding_box = _get_bounding_box(tdf)

        tiles = tilers.tiler.get(tiles_shape, base_shape=bounding_box, meters=meters)

    # Map locations to tiles
    # We can not use tdf.mapping from scikit-mobility because it does not accept Multipolygons

    # mtdf = tdf.mapping(tiles, remove_na=True)
    mtdf = _mapping(tdf, tiles, remove_na=True)

    return mtdf, tiles
