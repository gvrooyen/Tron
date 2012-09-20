__author__ = 'gvrooyen'

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from constants import *

class WorldMap(object):

    def __init__(self, world_size=30):
        plt.clf()
        self.world_size = world_size
        self.world_map = Basemap(projection='vandg',lat_0=0,lon_0=0)
        self.world_map.drawparallels(np.arange(-90.0,91.0,180.0/(world_size-1.0)),latmax=90)
        self.world_map.drawmeridians(np.arange(0,360,(360.0/world_size)),latmax=90)

    def tron_to_lonlat(self, tx, ty):
        lat = 180.0/(self.world_size-1.0)*ty - 90.0
        lon = (360.0/self.world_size)*tx
        return (lon, lat)

    def tron_to_xy(self, tx, ty):
        (lon,lat) = self.tron_to_lonlat(tx, ty)
        return self.world_map(lon,lat)

    def _plot_trace(self, trace, color):
        if len(trace) > 0:
            x,y = self.tron_to_xy(trace[0][0],trace[0][1])
            self.world_map.plot(x,y,color+'o',markersize=8.0)
            if len(trace) > 1:
                lon0,lat0 = self.tron_to_lonlat(trace[0][0],trace[0][1])
                for pos in trace[1:]:
                    lon,lat = self.tron_to_lonlat(pos[0],pos[1])
                    if (lon0 == 180.0) and (lon >= 180.0):
                        self.world_map.drawgreatcircle(lon0+0.001,lat0,lon+0.001,lat,linewidth=5,color=color)
                    elif (lon0 >= 180.0) and (lon == 180.0):
                        self.world_map.drawgreatcircle(lon0+0.001,lat0,lon+0.001,lat,linewidth=5,color=color)
                    else:
                        self.world_map.drawgreatcircle(lon0,lat0,lon,lat,linewidth=5,color=color)
                    lon0,lat0 = lon,lat
                if trace[-1][0] >= 15:
                    x,y = self.tron_to_xy(trace[-1][0]+0.001,trace[-1][1])
                else:
                    x,y = self.tron_to_xy(trace[-1][0],trace[-1][1])
                self.world_map.plot(x,y,color+'D',markersize=8.0)

    def plot_trace(self, trace1=None, trace2=None, player1=BLUE, player2=RED):

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

        self._plot_trace(trace1,p1color)
        self._plot_trace(trace2,p2color)

    def plot_points(self, points, color='k'):
        for point in points:
            x,y = self.tron_to_xy(point[0]+0.001,point[1])
            self.world_map.plot(x,y,color+'s',markersize=6.0)

    def show(self, title = None):
        if title:
            plt.title(title)
        plt.show()

    def save(self, title = None, filename = 'world.png'):
        if title:
            plt.title(title)
        fig = plt.gcf()
        fig.set_size_inches(16,12)
        plt.savefig(filename, dpi=100)
