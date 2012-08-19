__author__ = 'gvrooyen'

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

def plot_trace(trace=None, color='b', world_size=30):
    map = Basemap(projection='vandg',lat_0=0,lon_0=0,resolution=None)
    map.drawparallels(np.arange(-90.0,91.0,180.0/(world_size-1.0)),latmax=90)
    map.drawmeridians(np.arange(0,360,(360.0/world_size)),latmax=90)
    map.drawgreatcircle(0,0,0,20,linewidth=5,color='b')
    map.drawgreatcircle(0,20,20,20,linewidth=5,color='b')
    plt.show()


if __name__ == '__main__':
    plot_trace()
