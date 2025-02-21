#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "../external/sgtsnepi/src/sgtsne.cpp"

namespace py = pybind11;

std::vector<double> GLOBAL_GRID_SIZES;
int N_GRID_SIZE = 0;
int *listGridSize = NULL;
int GRID_SIZE_THRESHOLD = 0;

py::array_t<double, py::array::c_style> _sgtsnepi_c(
			 py::array_t<uint32_t, py::array::c_style> rows,
			 py::array_t<uint32_t, py::array::c_style> cols,
			 py::array_t<  double, py::array::c_style> vals,
			 py::array_t<  double, py::array::c_style> y_in,
			 int nnz,
			 int d,
			 double lambda_par,
			 int max_iter,
			 int early_exag,
			 int alpha,
			 bool fftw_single,
			 py::array_t<double> h,
			 double bb,
			 double eta,
			 int n,
			 bool drop_leaf,
			 bool run_exact,
			 int grid_threshold
		) {

		py::array_t<double, py::array::c_style> y({n,d});

		double *res = tsnepi_c(
				NULL, // time info, used for profiling
				NULL, // grid sizes, used for profiling
				rows.data(),
				cols.data(),
				vals.data(),
				y_in.mutable_data(),
				nnz,
				d,
				lambda_par,
				max_iter,
				early_exag,
				alpha,
				fftw_single,
				h.mutable_data(),
				bb,
				eta,
				NULL,
				0,
				n,
				drop_leaf,
				run_exact,
				grid_threshold,
				0 // number of processes. not useful in this case
		);

		std::copy(res, res + n * d, y.mutable_data());

		return y;
}

PYBIND11_MODULE(_sgtsnepi_, m) {
		m.def("_sgtsnepi_c", &_sgtsnepi_c);
}
