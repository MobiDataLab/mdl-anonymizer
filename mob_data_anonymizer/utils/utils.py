import psutil
from shapely import geometry
import geopandas as gpd
from skmob.utils.constants import DEFAULT_CRS


def inclusive_range(start, stop, step):
    if step:
        return range(start, (stop + 1) if step >= 0 else (stop - 1), step)
    else:
        return range(start, stop + 1)


def round_tuple(t: tuple, precision: int = 2):
    r = [round(v, precision) for v in t]

    return tuple(r)


def build_bounding_box(min_lng: float, min_lat: float, max_lng: float, max_lat: float):
    point_list = [[max_lng, max_lat], [max_lng, min_lat], [min_lng, min_lat], [min_lng, max_lat]]

    poly = geometry.Polygon(point_list)
    polygon = gpd.GeoDataFrame(index=[0], crs=DEFAULT_CRS, geometry=[poly])

    return polygon


def memory():
    mem = psutil.virtual_memory()
    available = mem.available
    available /= (1024 * 1024)  # MB

    return available


def memory_p(s):
    mem = psutil.virtual_memory()
    available = mem.available
    available /= (1024 * 1024)  # MB
    print(f"{s}: {available:.2f}")

    return available
