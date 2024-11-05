from .context import sgtsnepi

import sys

import numpy as np
import numpy.random

from scipy.io import mmread
from scipy.sparse import csc_matrix

import matplotlib.pyplot as plt


if __name__ == '__main__':
    mm_filename = sys.argv[1]

    with open(mm_filename) as mm_file:
        P = csc_matrix(mmread(mm_file))

    n = P.shape[0]
    n_dim = int(sys.argv[2])

    y = sgtsnepi.sgtsne._sgtsnepi_c(P, d=n_dim, h=0.7)

    if n_dim == 2:
        fig = plt.figure()
        ax = fig.add_subplot()

        ax.scatter(y[0], y[1])

        plt.show()

    if n_dim == 3:
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        ax.scatter(y[0], y[1], y[2])

        plt.show()
