#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/numpy.h>
#include <cstdio>

#include "sgtsne.cpp"

namespace py = pybind11;

py::array_t<double, py::array::c_style> sgtsnepi_c(
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
			 int grid_threshold,
			 bool silent
		) {

		py::object sys_stdout = py::module::import("sys").attr("stdout");
    py::object sys_stderr = py::module::import("sys").attr("stderr");
    py::object StringIO = py::module::import("io").attr("StringIO");

		py::object output_target;
		py::object error_target;

		if(silent) {
			// Discard output by redirecting to a dummy StringIO
			output_target = StringIO();
			error_target = StringIO();
		} else {
			// Use Python's sys.stdout
			output_target = sys_stdout;
			error_target = sys_stderr;
		}

		// Redirect stdout to output_target
		py::scoped_ostream_redirect out(std::cout, output_target);
		py::scoped_ostream_redirect err(std::cerr, error_target);

		py::array_t<double, py::array::c_style> y({n,d});

		// Redirect C-style stdout and stderr
    FILE* original_stdout = stdout;
    FILE* original_stderr = stderr;
    if (silent) {
        // Redirect stdout and stderr to /dev/null (Unix) or NUL (Windows)
        #ifdef _WIN32
            freopen("NUL", "w", stdout);
            freopen("NUL", "w", stderr);
        #else
            freopen("/dev/null", "w", stdout);
            freopen("/dev/null", "w", stderr);
        #endif
    }

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

		// Cleanup
		delete [] res;

		// Restore original stdout and stderr
    if (silent) {
        #ifdef _WIN32
            freopen("CON", "w", stdout);  // Restore stdout on Windows
            freopen("CON", "w", stderr);  // Restore stderr on Windows
        #else
            freopen("/dev/tty", "w", stdout);  // Restore stdout on Unix
            freopen("/dev/tty", "w", stderr);  // Restore stderr on Unix
        #endif
    }

		return y;
}

PYBIND11_MODULE(_sgtsnepi, m) {
		m.def("sgtsnepi_c", &sgtsnepi_c);
}
