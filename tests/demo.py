import sys

from scipy.io import mmread
from scipy.sparse import csc_matrix

import matplotlib.pyplot as plt

from .context import sgtsnepi
from sgtsnepi import sgtsnepi

if __name__ == '__main__':
    mm_filename = sys.argv[1]

    with open(mm_filename, 'r', encoding='utf-8') as mm_file:
        P = csc_matrix(mmread(mm_file))

    n = P.shape[0]
    n_dim = int(sys.argv[2])

    y = sgtsnepi(P, d=n_dim, h=0.7)

    if n_dim == 2:
        fig = plt.figure()
        ax = fig.add_subplot()

        ax.scatter(y[0], y[1], s=0.5)

        plt.show()

    if n_dim == 3:
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        ax.scatter(y[0], y[1], y[2], s=0.5)

        plt.show()
