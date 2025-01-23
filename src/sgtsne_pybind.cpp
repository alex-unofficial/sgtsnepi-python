#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "../external/sgtsnepi/src/sgtsne.cpp"

namespace py = pybind11;

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
			 py::array_t<double, py::array::c_style> h,
			 double bb,
			 double eta,
			 py::array_t<int32_t, py::array::c_style> list_grid_sizes,
			 int n_grid_sizes,
			 int n,
			 bool drop_leaf,
			 bool run_exact,
			 int grid_threshold
		) {

		py::array_t<double, py::array::c_style> y({n,d});


		// numpy.array(None) is (for some reason) translated
		// as NaN in C++ with pybind11. see the github issue
		// https://github.com/pybind/pybind11/issues/1953
		double *y_in_ptr = NULL;
		if (!isnan(y_in.data()[0])) {
			y_in_ptr = y_in.mutable_data();
		}

		double *res = tsnepi_c(
				NULL, // time info, used for profiling
				NULL, // grid sizes, used for profiling
				rows.data(),
				cols.data(),
				vals.data(),
				y_in_ptr,
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
				list_grid_sizes.data(),
				n_grid_sizes,
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
