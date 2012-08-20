__author__ = 'gvrooyen'

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from constants import *

def tron_to_lonlat(tx,ty, world_size=30):
    lat = 180.0/(world_size-1.0)*ty - 90.0
    lon = (360.0/world_size)*tx
    return (lon,lat)

def tron_to_xy(tx,ty,map,world_size=30):
    (lon,lat) = tron_to_lonlat(tx,ty,world_size)
    return map(lon,lat)

def _plot_trace(trace,color,map):
    if len(trace) > 0:
        x,y = tron_to_xy(trace[0][0],trace[0][1],map)
        map.plot(x,y,color+'o',markersize=8.0)
        if len(trace) > 1:
            lon0,lat0 = tron_to_lonlat(trace[0][0],trace[0][1])
            for pos in trace[1:]:
                lon,lat = tron_to_lonlat(pos[0],pos[1])
                map.drawgreatcircle(lon0,lat0,lon,lat,linewidth=5,color=color)
                lon0,lat0 = lon,lat
            x,y = tron_to_xy(trace[-1][0],trace[-1][1],map)
            map.plot(x,y,color+'D',markersize=8.0)

def plot_trace(trace1=None, trace2=None, player1=BLUE, player2=RED, world_size=30):
    map = Basemap(projection='vandg',lat_0=0,lon_0=0,resolution=None)
    map.drawparallels(np.arange(-90.0,91.0,180.0/(world_size-1.0)),latmax=90)
    map.drawmeridians(np.arange(0,360,(360.0/world_size)),latmax=90)
#    map.drawgreatcircle(0,0,0,20,linewidth=5,color='b')
#    map.drawgreatcircle(0,20,20,20,linewidth=5,color='b')
#    x,y = map(0,0)
#    map.plot(x,y,'bo',markersize=8.0)
#    x,y = map(20,20)
#    map.plot(x,y,'bD',markersize=8.0)
#    plt.show()

    if player1 == BLUE:
        p1color = 'b'
    elif player1 == RED:
        p1color = 'r'
    else:
        p1color = 'm'

    if player2 == BLUE:
        p2color = 'b'
    elif player2 == RED:
        p2color = 'r'
    else:
        p2color = 'm'

    _plot_trace(trace1,p1color,map)
    _plot_trace(trace2,p2color,map)

    plt.show()


if __name__ == '__main__':
    plot_trace()
