# SG-t-SNE-Π wrapper for Python

This repository aims to provide a `Python` interface to 
[SG-t-SNE-Π](http://t-sne-pi.cs.duke.edu), which is a high-performance 
software for swift embedding of a large, sparse graph into
a d-dimensional space (d=1,2,3) on a shared-memory computer.

> :warning: **Warning!** This repository is still a work in progress and is not ready for general use.

### Prerequisites

SG-t-SNE-Π uses the following open-source software:

-   [FFTW3](http://www.fftw.org/) 3.3.8
-   [METIS](http://glaros.dtc.umn.edu/gkhome/metis/metis/overview) 5.1.0
-   [FLANN](https://www.cs.ubc.ca/research/flann/) 1.9.1
-   [Intel TBB](https://01.org/tbb) 2019
-   [LZ4](https://github.com/lz4/lz4) 1.9.1
-   [Doxygen](http://www.doxygen.nl/) 1.8.14

Before installing the module you must install the software dependencies
with your package manager of choice.

On Ubuntu:
```sh
sudo apt-get install libtbb-dev libflann-dev libmetis-dev libfftw3-dev liblz4-dev doxygen
```

On macOS:
```sh
brew install flann tbb metis fftw lz4 doxygen
```

## Installation

As of this point in the development it is recommended to work inside of a
`Python` [virtual environment](https://docs.python.org/3/library/venv.html)

To install the package run
```sh
pip install git+https://github.com/alex-unofficial/sgtsnepi-python.git
```

Then in your Python code run the following to import the library:
```python
import sgtsnepi

# [ ... ]

sgtsnepi.sgtsnepi(sparse_matrix, args)
```

Or to import the `sgtsnepi` function directly:
```python
from sgtsnepi import sgtsnepi

# [ ... ]

sgtsnepi(sparse_matrix, args)
```

## Running the Demo

To use the demo you should install [matplotlib](https://matplotlib.org/) by running
```sh
pip install matplotlib
```

Then from the source directory run
```
python tests/demo.py mm_file.mtx ndim
```
where `mm_file.mtx` is a file containing the input matrix which is in the
[Matrix Market](https://math.nist.gov/MatrixMarket/index.html) file format,
and `ndim` is the number of embedding dimensions.

## Citation

If you use this software, pleace cite the following paper:

```bibtex
@inproceedings{pitsianis2019sgtsnepi,
    author = {Pitsianis, Nikos and Iliopoulos, Alexandros-Stavros and Floros, Dimitris and Sun,        Xiaobai},
    doi = {10.1109/HPEC.2019.8916505},
    booktitle = {IEEE High Performance Extreme Computing Conference},
    month = {11},
    title = {{Spaceland Embedding of Sparse Stochastic Graphs}},
    year = {2019}
}
```
