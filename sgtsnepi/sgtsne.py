from math import inf

import numpy
from scipy.sparse import csc_matrix

from nextprod import nextprod

from . import _sgtsnepi

def sgtsnepi(
    input_graph, y0=None, d=2, max_iter=1000, early_exag=250,
    lambda_par=1, h=1.0, bb=-1.0, eta=200.0, run_exact=False,
    fftw_single=False, alpha=12, drop_leaf=False,
    grid_threshold=None, silent=False
):

    # Import input_graph as CSC matrix
    try:
        input_graph = csc_matrix(input_graph)
    except ValueError as e:
        raise TypeError("input_graph must be an adjacency matrix") from e

    if not input_graph.shape[0] == input_graph.shape[1]:
        raise ValueError("input_graph must be square")

    n = input_graph.shape[0]

    # Eliminate self-loops for input_matrix
    if any(input_graph.diagonal() != 0):
        print("Warning: input_graph has self-loops; setting distances to 0")

    input_graph.setdiag(numpy.zeros(n))
    input_graph.eliminate_zeros()

    nnz = input_graph.nnz

    if input_graph.data.size > 0 and numpy.min(input_graph.data) < 0:
        raise ValueError("Negative edge weights are not supported")

    if y0 is not None:
        try:
            y0 = numpy.array(y0)
        except Exception as e:
            raise TypeError("y0 must be array-like or None.") from e

        if y0.shape != (d, n):
            raise ValueError("y0 must be of shape (d, n)")

        y0 = numpy.transpose(y0)

    # Setting parameters correctly
    list_grid_sizes = [nextprod((2, 3, 5), x) for x in range(16, 512)]

    if grid_threshold is None:
        grid_threshold = 1e6 ** (1/d)

    grid_threshold = int(grid_threshold)

    bb = inf if run_exact else bb
    bb = h * (n ** (1/d)) / 2 if bb <= 0 else bb

    h = 1.0 if h == 0 else h
    h = [max_iter + 1, h]

    y = _sgtsnepi.sgtsnepi_c(
        numpy.array(input_graph.indices, dtype=numpy.uint32),
        numpy.array(input_graph.indptr, dtype=numpy.uint32),
        numpy.array(input_graph.data, dtype=numpy.float64),
        y0,
        nnz,
        d,
        lambda_par,
        max_iter,
        early_exag,
        alpha,
        fftw_single,
        numpy.array(h, dtype=numpy.float64),
        bb,
        eta,
        numpy.array(list_grid_sizes, dtype=numpy.int32),
        len(list_grid_sizes),
        n,
        drop_leaf,
        run_exact,
        grid_threshold,
        silent
    )

    # permute y to (d, n)
    y = numpy.transpose(y)

    return y
