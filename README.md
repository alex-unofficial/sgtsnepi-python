# SG-t-SNE-Π wrapper for Python

This repository aims to provide a `Python` interface to 
[SG-t-SNE-Π](http://t-sne-pi.cs.duke.edu), which is a high-performance 
software for swift embedding of a large, sparse graph into
a d-dimensional space (d=1,2,3) on a shared-memory computer.

> :warning: **Warning!** This package is still a work in progress.

## Installation

### Prerequisites

`sgtsnepi` supports Linux and macOS.
Windows support is coming soon.

Installation requires `Python 3.9` or higher.

Wheels are not built for all architectures as of now.
If your architecture is not supported please open a relevant issue on the GitHub page.

### Installing the Module

To install the package run
```sh
pip install sgtsnepi
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
pip install scipy matplotlib
```

Then from the source directory run
```
python tests/demo.py mm_file.mtx ndim
```
where `mm_file.mtx` is a file containing the input matrix which is in the
[Matrix Market](https://math.nist.gov/MatrixMarket/index.html) file format,
and `ndim` is the number of embedding dimensions.

You can find some compressed `MatrixMarket` files in the `data/` subdirectory.

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
