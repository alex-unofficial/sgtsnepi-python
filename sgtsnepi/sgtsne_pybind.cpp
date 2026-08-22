#include <algorithm>
#include <cmath>
#include <cstdio>
#include <iostream>
#include <memory>
#include <optional>
#include <sstream>
#include <utility>

#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/numpy.h>

#ifdef _WIN32
  #include <io.h>
  #include <fcntl.h>
  #define dup_        _dup
  #define dup2_       _dup2
  #define close_      _close
  #define fileno_     _fileno
  #define open_null_() _open("NUL", _O_WRONLY)
#else
  #include <unistd.h>
  #include <fcntl.h>
  #define dup_        dup
  #define dup2_       dup2
  #define close_      close
  #define fileno_     fileno
  #define open_null_() open("/dev/null", O_WRONLY)
#endif

#include "sgtsne.cpp"

namespace py = pybind11;

namespace {
// Silences the C-level stdout/stderr *file descriptors* for as long as it lives.
//
// Restores with dup2 rather than freopen. freopen closes the stream first and
// only then attempts the open, so a failed restore (freopen("/dev/tty", ...)
// with no controlling terminal -- any batch job, CI runner or nohup'd process)
// leaves the stream permanently closed, and every later write raises EBADF.
// dup2 also restores whatever the descriptor originally pointed at -- terminal,
// pipe or file -- instead of forcing it to the terminal and silently breaking
// shell redirection.
//
// Because the descriptors are never closed, their numbers never become
// available for reuse, so a concurrent open() in another thread cannot be
// handed fd 1 or 2 mid-call.
//
// RAII, so the restore also happens when the computation throws. A manual
// restore at the end of the function does not run on the exception path, and
// the process is then left writing to /dev/null forever -- silently.
class FdSilencer {
public:
    explicit FdSilencer(bool active) {
        if (!active) {
            return;
        }

        std::fflush(stdout);
        std::fflush(stderr);

        saved_out_ = dup_(fileno_(stdout));
        saved_err_ = dup_(fileno_(stderr));

        const int devnull = open_null_();
        if (devnull >= 0) {
            dup2_(devnull, fileno_(stdout));
            dup2_(devnull, fileno_(stderr));
            close_(devnull);
        } else {
            // Could not silence; drop the saved copies rather than leak them.
            restore();
        }
    }

    ~FdSilencer() { restore(); }

    FdSilencer(const FdSilencer &) = delete;
    FdSilencer &operator=(const FdSilencer &) = delete;
    FdSilencer(FdSilencer &&) = delete;
    FdSilencer &operator=(FdSilencer &&) = delete;

private:
    void restore() {
        if (saved_out_ >= 0) {
            std::fflush(stdout);
            dup2_(saved_out_, fileno_(stdout));
            close_(saved_out_);
            saved_out_ = -1;
        }
        if (saved_err_ >= 0) {
            std::fflush(stderr);
            dup2_(saved_err_, fileno_(stderr));
            close_(saved_err_);
            saved_err_ = -1;
        }
    }

    int saved_out_ = -1;
    int saved_err_ = -1;
};

// Redirects the C++ iostreams for as long as it lives.
//
//   silent    -> a local std::ostringstream. No Python object is involved, so
//                the GIL can be released around the computation.
//   otherwise -> Python's sys.stdout / sys.stderr, so output appears in
//                notebooks and captured test output. Touching Python means the
//                GIL must stay held for the duration.
class StreamRedirect {
public:
    StreamRedirect(bool silent, const py::object &py_out, const py::object &py_err) {
        if (silent) {
            old_out_ = std::cout.rdbuf(sink_.rdbuf());
            old_err_ = std::cerr.rdbuf(sink_.rdbuf());
        } else {
            out_.emplace(std::cout, py_out);
            err_.emplace(std::cerr, py_err);
        }
    }

    ~StreamRedirect() {
        if (old_out_ != nullptr) {
            std::cout.rdbuf(old_out_);
        }
        if (old_err_ != nullptr) {
            std::cerr.rdbuf(old_err_);
        }
        // out_ / err_ destruct after this body and need the GIL, which is held
        // here -- it is only released around the computation itself.
    }

    StreamRedirect(const StreamRedirect &) = delete;
    StreamRedirect &operator=(const StreamRedirect &) = delete;
    StreamRedirect(StreamRedirect &&) = delete;
    StreamRedirect &operator=(StreamRedirect &&) = delete;

private:
    std::ostringstream sink_;
    std::streambuf *old_out_ = nullptr;
    std::streambuf *old_err_ = nullptr;
    std::optional<py::scoped_ostream_redirect> out_;
    std::optional<py::scoped_ostream_redirect> err_;
};

}  // namespace

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
    py::object py_out;
    py::object py_err;
    if (!silent) {
        const py::module sys = py::module::import("sys");
        py_out = sys.attr("stdout");
        py_err = sys.attr("stderr");
    }

    StreamRedirect streams(silent, py_out, py_err);
    FdSilencer    fds(silent);

    py::array_t<double, py::array::c_style> y({n, d});

    // numpy.array(None) is translated as NaN in C++ by pybind11; see
    // https://github.com/pybind/pybind11/issues/1953
    double *y_in_ptr = nullptr;
    if (y_in.size() > 0 && !std::isnan(y_in.data()[0])) {
        y_in_ptr = y_in.mutable_data();
    }

    // Resolve every buffer pointer *before* releasing the GIL: the accessors
    // below touch Python objects. The arrays stay alive for the duration
    // because the caller holds references to them.
    const uint32_t *rows_ptr  = rows.data();
    const uint32_t *cols_ptr  = cols.data();
    const double   *vals_ptr  = vals.data();
    double         *h_ptr     = h.mutable_data();
    const int32_t  *grid_ptr  = list_grid_sizes.data();

    auto run = [&]() -> double * {
        return tsnepi_c(
                nullptr,  // time info, used for profiling
                nullptr,  // grid sizes, used for profiling
                rows_ptr,
                cols_ptr,
                vals_ptr,
                y_in_ptr,
                nnz,
                d,
                lambda_par,
                max_iter,
                early_exag,
                alpha,
                fftw_single,
                h_ptr,
                bb,
                eta,
                grid_ptr,
                n_grid_sizes,
                n,
                drop_leaf,
                run_exact,
                grid_threshold,
                0  // number of processes; not useful here
        );
    };

    // unique_ptr so the buffer is freed on the exception path too.
    std::unique_ptr<double[]> res;
    if (silent) {
        // Safe: nothing inside touches a Python object while the GIL is down.
        // Releasing it lets Python threads -- a progress or memory-sampling
        // thread, say -- actually run during a long embed, and permits
        // concurrent embeds from several threads.
        py::gil_scoped_release nogil;
        res.reset(run());
    } else {
        // The iostreams are wired to Python objects; the GIL must stay held.
        res.reset(run());
    }

    std::copy(res.get(), res.get() + static_cast<std::size_t>(n) * d, y.mutable_data());

    return y;
}

PYBIND11_MODULE(_sgtsnepi, m) {
    m.def("sgtsnepi_c", &sgtsnepi_c);
}
