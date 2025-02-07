import numpy as np
import scipy.sparse as sp

from sgtsnepi.sgtsne import sgtsnepi

if __name__ == '__main__':

    # Some input array
    y_in = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])

    # P does not matter here since we are not doing any work.
    P = sp.random(4, 4, density=0.1)

    # Using max_iter = 0 we simply return the input array
    y = sgtsnepi(P, y_in, d=2, max_iter=0, silent=True)

    # Test that the input and output arrays are exactly equal
    if np.any(y != y_in):
        print('array mismatch!')
    else:
        print('success!')

