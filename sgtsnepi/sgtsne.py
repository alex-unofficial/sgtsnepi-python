import os

from ctypes import CDLL
from ctypes import c_int, c_double, c_uint32, POINTER

from math import inf

import pkg_resources

import numpy
import numpy.ctypeslib

from scipy.sparse import csc_matrix

from nextprod import nextprod


# Pointer type definitions
c_int_p = POINTER(c_int)
c_uint32_p = POINTER(c_uint32)
c_double_p = POINTER(c_double)
c_double_pp = POINTER(c_double_p)

# Correctly set LD_LIBRARY_PATH
package_dir = pkg_resources.resource_filename('sgtsnepi', 'lib')
os.environ['LD_LIBRARY_PATH'] = package_dir

# Importing tsnepi_c from the compiled shared object library
libsgtsne = CDLL(os.path.join(package_dir, 'libsgtsnepi.so.0'))

libsgtsne.tsnepi_c.argtypes = [
    c_double_pp, c_double_p,
    c_uint32_p, c_uint32_p, c_double_p, c_double_p, c_int,
    c_int, c_double, c_int, c_int,
    c_double, c_int, c_double_p, c_double, c_double,
    c_int_p, c_int,
    c_int, c_int, c_int,
    c_int, c_int
]
libsgtsne.tsnepi_c.restype = c_double_p


def sgtsnepi(
    input_graph, y0=None, d=2, max_iter=1000, early_exag=250,
    lambda_par=1, num_proc=0, h=1.0, bb=-1.0, eta=200.0, run_exact=False,
    fftw_single=False, alpha=12, profile=False, drop_leaf=False,
    list_grid_sizes=[nextprod((2, 3, 5), x) for x in range(16, 512)],
    grid_threshold=None
):

    # Import input_graph as CSC matrix
    try:
        input_graph = csc_matrix(input_graph)
    except ValueError as e:
        raise TypeError("input_graph must be an adjacency matrix") from e

    if not input_graph.shape[0] == input_graph.shape[1]:
        raise ValueError("input_graph must be symmetric")

    n = input_graph.shape[0]

    # Eliminate self-loops for input_matrix
    if any(input_graph.diagonal() != 0):
        print("Warning: input_graph has self-loops; setting distances to 0")
    input_graph.setdiag(numpy.zeros(n))
    input_graph.eliminate_zeros()

    if numpy.min(input_graph.data) < 0:
        raise ValueError("Negative edge weights are not supported")

    if y0 is not None:
        try:
            y0 = numpy.array(y0)
        except Exception as e:
            raise TypeError("y0 must be array-like or None.") from e

        if y0.shape != (d, n):
            raise ValueError("y0 must be of shape (d, n)")

    return _sgtsnepi_c(input_graph, y0, d, max_iter, early_exag, lambda_par,
                       num_proc, h, bb, eta, run_exact, fftw_single, alpha,
                       profile, drop_leaf, list_grid_sizes, grid_threshold)


def _sgtsnepi_c(
    input_graph, y0=None, d=2, max_iter=1000, early_exag=250,
    lambda_par=1, num_proc=0, h=1.0, bb=-1.0, eta=200.0, run_exact=False,
    fftw_single=False, alpha=12, profile=False, drop_leaf=False,
    list_grid_sizes=[nextprod((2, 3, 5), x) for x in range(16, 512)],
    grid_threshold=None
):

    # Assign memory for profile information buffers
    time_info = ((c_double * 6) * max_iter)()
    if profile:
        ptr_time_info = (c_double_p * max_iter)()
        for i in range(max_iter):
            ptr_time_info[i] = time_info[i][0]
    else:
        ptr_time_info = None

    grid_sizes = None

    # extract CSC data from input_graph
    n = input_graph.shape[0]
    nnz = input_graph.nnz

    ptr_rows = input_graph.indices.ctypes.data_as(c_uint32_p)
    ptr_cols = input_graph.indptr.ctypes.data_as(c_uint32_p)
    ptr_vals = input_graph.data.ctypes.data_as(c_double_p)

    # Create y0 pointer
    ptr_y0 = None if y0 is None else y0.T.ctypes.data_as(c_double_p)

    # Setting parameters correctly
    if grid_threshold is None:
        grid_threshold = 1e6 ** (1/d)

    grid_threshold = int(grid_threshold)

    bb = inf if run_exact else bb
    bb = h * (n ** (1/d)) / 2 if bb <= 0 else bb

    h = 1.0 if h == 0 else h
    h = (c_double * 2)(max_iter + 1, h)

    list_grid_sizes_len = len(list_grid_sizes)
    list_grid_sizes = (c_int * list_grid_sizes_len)(*list_grid_sizes)

    print("Entering into C...")

    # Running the C function
    ptr_y = libsgtsne.tsnepi_c(
        ptr_time_info, grid_sizes,
        ptr_rows, ptr_cols, ptr_vals, ptr_y0, nnz,
        d, lambda_par, max_iter, early_exag,
        alpha, fftw_single, h, bb, eta,
        list_grid_sizes, list_grid_sizes_len,
        n, drop_leaf, run_exact,
        grid_threshold, num_proc
    )

    print("Back to Python...")

    # Extract the data from the c_double pointer to a numpy array
    y = numpy.ctypeslib.as_array(ptr_y, shape=(n, d)).T

    if profile:
        return y, time_info

    return y
