import matplotlib.pyplot as plt
import numpy as np


xs__ = np.array([610, 666, 729, 792, 816, 816, 817, 818, 831, 856, 869, 872, 850, 791, 725, 643, 573, 535, 505, 502, 517])
ys__ = np.array([308, 313, 298, 286, 283, 284, 289, 309, 349, 400, 438, 454, 461, 470, 475, 489, 484, 486, 494, 483, 450])


def findEdge(xs, ys):
    x_max = xs.max()
    y_max = ys.max()
    x_min = xs.min()
    y_min = ys.min()

    A1, B1, C1 = 1, 0, -x_max
    A2, B2, C2 = 0, 1, -y_max
    A3, B3, C3 = 1, 0, -x_min
    A4, B4, C4 = 0, 1, -y_min

    return np.array((A1, B1, C1), (A2, B2, C2), (A3, B3, C3), (A4, B4, C4))


if __name__ == '__main__':
    l1, l2, l3, l4 = findEdge(xs__, ys__)

    plt.scatter(xs__, ys__)
    plt.show()

