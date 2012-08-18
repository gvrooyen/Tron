__author__ = 'gvrooyen'

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

def plot_trace(world_size=30):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d', aspect='equal')

    u = np.linspace(0, 2 * np.pi, world_size*10)
    v = np.linspace(0, np.pi, world_size*10)

    x = 10 * np.outer(np.cos(u), np.sin(v))
    y = 10 * np.outer(np.sin(u), np.sin(v))
    z = 10 * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z,  rstride=4, cstride=4, color='b')

    plt.show()

if __name__ == '__main__':
    plot_trace()
