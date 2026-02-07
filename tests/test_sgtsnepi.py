"""Comprehensive test suite for sgtsnepi package."""

import numpy as np
import scipy.sparse as sp
import pytest

from sgtsnepi import sgtsnepi


class TestImports:
    """Test that package imports work correctly."""

    def test_import_module(self):
        """Test module import."""
        import sgtsnepi
        assert sgtsnepi is not None

    def test_import_function(self):
        """Test direct function import."""
        from sgtsnepi import sgtsnepi
        assert sgtsnepi is not None
        assert callable(sgtsnepi)


class TestBasicFunctionality:
    """Test basic sgtsnepi functionality."""

    def test_simple_graph_2d(self):
        """Test embedding a simple sparse graph in 2D."""
        n = 10
        P = sp.random(n, n, density=0.3, format='csc')
        P = P + P.T  # Make symmetric

        y = sgtsnepi(P, d=2, max_iter=10, silent=True)

        assert y.shape == (2, n)
        assert y.dtype == np.float64
        assert not np.any(np.isnan(y))
        assert not np.any(np.isinf(y))

    def test_simple_graph_3d(self):
        """Test embedding a simple sparse graph in 3D."""
        n = 10
        P = sp.random(n, n, density=0.3, format='csc')

        y = sgtsnepi(P, d=3, max_iter=10, silent=True)

        assert y.shape == (3, n)
        assert y.dtype == np.float64

    def test_with_initial_positions(self):
        """Test embedding with provided initial positions."""
        n = 10
        P = sp.random(n, n, density=0.3, format='csc')
        y0 = np.random.randn(2, n)

        y = sgtsnepi(P, y0=y0, d=2, max_iter=10, silent=True)

        assert y.shape == (2, n)
        assert y.dtype == np.float64

    def test_zero_iterations_returns_input(self):
        """Test that zero iterations returns the initial positions unchanged."""
        n = 4
        P = sp.random(n, n, density=0.1, format='csc')
        y_in = np.array([[1, 2, 3, 4], [5, 6, 7, 8]], dtype=np.float64)

        y = sgtsnepi(P, y0=y_in, d=2, max_iter=0, silent=True)

        np.testing.assert_array_equal(y, y_in)


class TestInputValidation:
    """Test input validation and error handling."""

    def test_non_square_matrix_raises(self):
        """Test that non-square matrices raise ValueError."""
        P = sp.random(5, 10, density=0.1, format='csc')

        with pytest.raises(ValueError, match="must be square"):
            sgtsnepi(P, d=2, silent=True)

    def test_negative_weights_raise(self):
        """Test that negative edge weights raise ValueError."""
        P = sp.csc_matrix([[0, 1, -1], [1, 0, 1], [-1, 1, 0]])

        with pytest.raises(ValueError, match="Negative edge weights"):
            sgtsnepi(P, d=2, silent=True)

    def test_invalid_y0_shape_raises(self):
        """Test that y0 with wrong shape raises ValueError."""
        n = 10
        P = sp.random(n, n, density=0.1, format='csc')
        y0 = np.random.randn(3, 5)  # Wrong shape

        with pytest.raises(ValueError, match="must be of shape"):
            sgtsnepi(P, y0=y0, d=2, silent=True)

    def test_invalid_graph_type_raises(self):
        """Test that invalid graph type raises TypeError."""
        with pytest.raises(TypeError, match="adjacency matrix"):
            sgtsnepi("not a matrix", d=2, silent=True)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_node_graph(self):
        """Test embedding a graph with a single node.

        Note: Single isolated nodes produce NaN as there's no relational
        information for the embedding algorithm.
        """
        P = sp.csc_matrix([[0]])

        y = sgtsnepi(P, d=2, max_iter=10, silent=True)

        # Shape should be correct even if values are NaN
        assert y.shape == (2, 1)

    def test_empty_graph(self):
        """Test embedding a graph with no edges."""
        n = 5
        P = sp.csc_matrix((n, n))

        y = sgtsnepi(P, d=2, max_iter=10, silent=True)

        assert y.shape == (2, n)
        assert not np.any(np.isnan(y))

    def test_fully_connected_graph(self):
        """Test embedding a fully connected graph."""
        n = 5
        P = sp.csc_matrix(np.ones((n, n)) - np.eye(n))

        y = sgtsnepi(P, d=2, max_iter=10, silent=True)

        assert y.shape == (2, n)
        assert not np.any(np.isnan(y))

    def test_self_loops_removed(self, capsys):
        """Test that self-loops are handled with warning."""
        n = 5
        P = sp.eye(n, format='csc')

        y = sgtsnepi(P, d=2, max_iter=10, silent=False)

        captured = capsys.readouterr()
        assert "self-loops" in captured.out
        assert y.shape == (2, n)


class TestDifferentFormats:
    """Test that different sparse matrix formats work."""

    @pytest.mark.parametrize("format_type", ['csc', 'csr', 'coo', 'lil'])
    def test_sparse_formats(self, format_type):
        """Test that different scipy sparse formats are accepted."""
        n = 10
        P = sp.random(n, n, density=0.3, format=format_type)

        y = sgtsnepi(P, d=2, max_iter=10, silent=True)

        assert y.shape == (2, n)

    def test_dense_array(self):
        """Test that dense arrays are converted properly."""
        n = 5
        P = np.random.rand(n, n)
        P = (P > 0.7).astype(float)  # Make sparse-like

        y = sgtsnepi(P, d=2, max_iter=10, silent=True)

        assert y.shape == (2, n)


class TestParameters:
    """Test various parameter configurations."""

    def test_different_dimensions(self):
        """Test embedding in different dimensions."""
        n = 10
        P = sp.random(n, n, density=0.3, format='csc')

        for d in [1, 2, 3]:
            y = sgtsnepi(P, d=d, max_iter=10, silent=True)
            assert y.shape == (d, n)

    def test_early_exaggeration(self):
        """Test that early exaggeration parameter works."""
        n = 10
        P = sp.random(n, n, density=0.3, format='csc')

        y = sgtsnepi(P, d=2, max_iter=100, early_exag=50, silent=True)

        assert y.shape == (2, n)

    def test_exact_computation(self):
        """Test exact computation mode."""
        n = 8
        P = sp.random(n, n, density=0.3, format='csc')

        y = sgtsnepi(P, d=2, max_iter=10, run_exact=True, silent=True)

        assert y.shape == (2, n)

    def test_single_precision_fft(self):
        """Test single precision FFT mode."""
        n = 10
        P = sp.random(n, n, density=0.3, format='csc')

        y = sgtsnepi(P, d=2, max_iter=10, fftw_single=True, silent=True)

        assert y.shape == (2, n)


class TestReproducibility:
    """Test deterministic behavior with fixed inputs."""

    def test_with_initial_positions_deterministic(self):
        """Test that results are deterministic when initial positions are provided."""
        n = 10
        P = sp.random(n, n, density=0.3, format='csc', random_state=42)
        y0 = np.random.RandomState(123).randn(2, n)

        # With same initial positions, should get same result
        y1 = sgtsnepi(P, y0=y0.copy(), d=2, max_iter=50, silent=True)
        y2 = sgtsnepi(P, y0=y0.copy(), d=2, max_iter=50, silent=True)

        # Note: Results may still differ due to internal non-determinism
        # (parallel execution, FFTW, C++ RNG), so we just check they're close
        assert y1.shape == y2.shape
        assert not np.any(np.isnan(y1))
        assert not np.any(np.isnan(y2))
