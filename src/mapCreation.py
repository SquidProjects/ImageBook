import cv2
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import contextily
import matplotlib.pyplot as plt

from textOnImage import addTextToImage

def get_map_at_coordinates(Lat,Lon,radius,quality):
    """
    Creates an image of a map at the given location. Function requires internet acess to download the mapdata.

    Args:
        Lat (float): Latitude
        Lon (float): longitude
        radius (float): radius to display in km
        quality (_type_): Quality of the downloaded map: 0 = standard, 1 = higher quality, -1 = lower quality

    Returns:
        opencv img: map as image
    """
    radius=radius*1000

    # convert the point to geo coordinates
    geo = {'col1': ['P1'], 'geometry': [Point(Lon,Lat)]}# lat lon need to be switched here
    geodf = gpd.GeoDataFrame(geo, crs="EPSG:4326")
    data = geodf.to_crs(epsg=3857)

    # create a plot
    fig, ax = plt.subplots(figsize=(25,20)) 
    data.plot(ax=ax, color='red', marker='v', markersize=5000)
    ax.axis('off')

    # set the radius
    bounds = data.total_bounds
    ax.set_xlim(bounds[0]-radius, bounds[2]+radius)
    ax.set_ylim(bounds[1]-radius, bounds[3]+radius)
    
    #get map from openStreetMap
    provider = contextily.providers.OpenStreetMap.Mapnik
    zoom_level = int(round(-1.302883*np.log(radius)+24) + quality)

    contextily.add_basemap(ax, zoom=zoom_level, source=provider,
                           crs=data.crs.to_string())
    fig.tight_layout()
    fig.canvas.draw()

    # Now we can save it to a numpy array.
    cv_image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    cv_image = cv_image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
    return cv_image

class Map:
    def __init__(self, map_string):
            if not self.is_map(map_string):
                raise ValueError("Given string is not a map")
            self.lat, self.lon, self.radius = [float(element) for element in map_string[len("%map"):].split(",")]
            if self.lat>90.0 or self.lat < -90.0 or self.lon>180.0 or self.lon<-180.0 or self.radius<=0:
                raise ValueError(f"map coordinates are worng. Got lat{self.lat} lon {self.lon} radius {self.radius} Expect -90<lat<90 and -180<lon<180 and radius > 0")
            
    @staticmethod
    def is_map(map_string):
        if map_string.find("%map")>=0:
            return True
        return False
    
    def generate_img(self,description, print_settings):
        map = get_map_at_coordinates(self.lat,self.lon, self.radius,print_settings.map_quality)
        map = addTextToImage(map, description, print_settings)
        return map