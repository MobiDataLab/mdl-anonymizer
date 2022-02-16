import folium
import matplotlib
import skmob
from geopandas import GeoDataFrame
from matplotlib import cm
from pandas import merge
from shapely import geometry
from skmob.tessellation import tilers
from skmob.utils.constants import DEFAULT_CRS


def color_map_color(value, cmap_name='magma', vmin=0, vmax=1000):
    # norm = plt.Normalize(vmin, vmax)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap(cmap_name)  # PiYG
    rgb = cmap(norm(abs(value)))[:3]  # will return rgba, we take only first 3 so we get rgb
    color = matplotlib.colors.rgb2hex(rgb)
    return color

def get_bounding_box(tdf):
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



#maploc = folium.Map(zoom_start=10, tiles='cartodbpositron')
#folium.GeoJson(tessellation).add_to(maploc)
# maploc.save('maps/tesselation.html')


tdf = skmob.TrajDataFrame.from_file('../anonymize/out/actual_dataset_loaded.csv', latitude='lat', longitude='lon', datetime='timestamp', user_id='user_id')




bounding_box = get_bounding_box(tdf)

tessellation = tilers.tiler.get("squared", base_shape=bounding_box, meters=500)

mtdf = tdf.mapping(tessellation)
# count the points in each zone:
points = mtdf['tile_ID'].value_counts(dropna=False)


# join with the tessellation
pp = points.rename_axis('tile_ID').reset_index(name='count')
max = pp['count'].max()
min = pp['count'].min()
t = merge(tessellation, pp, how='left', on='tile_ID')
t2 = t.fillna(0)
maploc = folium.Map(tiles='cartodbpositron', control_scale = True)

sw = tdf[['lat', 'lng']].min().values.tolist()
ne = tdf[['lat', 'lng']].max().values.tolist()

maploc.fit_bounds([sw, ne])

folium.GeoJson(t2, style_function=lambda feature: {

        'fill': True,
        'color': color_map_color(feature['properties']['count'], vmin=min, vmax=max),
        'weight' : 0.3,
        'fillOpacity' : 0.5,
        'label': "abcd"
        }).add_to(maploc)

maploc.save('maps/tesselation.html')