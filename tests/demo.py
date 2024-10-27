from .context import sgtsnepi

import sys

from scipy.io import mmread
from scipy.sparse import csc_matrix

import matplotlib.pyplot as plt


if __name__ == '__main__':
    mm_filename = sys.argv[1]

    with open(mm_filename) as mm_file:
        P = csc_matrix(mmread(mm_file))

    y = sgtsnepi.sgtsne._sgtsnepi_c(P, h=0.7)

    plt.figure()
    plt.scatter(y[0], y[1], 0.5)
    plt.show()
