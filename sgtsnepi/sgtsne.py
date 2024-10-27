from ctypes import CDLL
from ctypes.util import find_library

from ctypes import c_int, c_double, c_uint32, POINTER

from math import inf

import numpy
import numpy.ctypeslib

from nextprod import nextprod


# Pointer type definitions
c_int_p = POINTER(c_int)
c_uint32_p = POINTER(c_uint32)
c_double_p = POINTER(c_double)
c_double_pp = POINTER(c_double_p)

# Importing tsnepi_c from the compiled shared object library
libsgtsne = CDLL(find_library('sgtsnepi'))

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


def _sgtsnepi_c(
        input_graph, y0=None, d=2, max_iter=1000, early_exag=250, lambda_par=1,
        np=0, h=1.0, bb=-1.0, eta=200.0, run_exact=False, fftw_single=False,
        alpha=12, profile=False, drop_leaf=False,
        list_grid_sizes = [nextprod((2, 3, 5), x) for x in range(16,512)],
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
    ptr_y0 = None if y0 is None else y0.ctypes.data_as(c_double_p)

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

    # Running the C function
    ptr_y = libsgtsne.tsnepi_c(
        ptr_time_info, grid_sizes,
        ptr_rows, ptr_cols, ptr_vals, ptr_y0, nnz,
        d, lambda_par, max_iter, early_exag,
        alpha, fftw_single, h, bb, eta,
        list_grid_sizes, list_grid_sizes_len,
        n, drop_leaf, run_exact,
        grid_threshold, np
    )

    # Extract the data from the c_double pointer to a numpy array
    y = numpy.ctypeslib.as_array(ptr_y, shape=(d, n))

    if profile:
        return y, time_info

    return y
