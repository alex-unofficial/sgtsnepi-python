# SG-t-SNE-Π wrapper for Python

This repository aims to provide a `Python` interface to 
[SG-t-SNE-Π](http://t-sne-pi.cs.duke.edu), which is a high-performance 
software for swift embedding of a large, sparse graph into
a d-dimensional space (d=1,2,3) on a shared-memory computer.

[!WARNING]
This repository is still a work in progress and is not ready for general use.

## Installation

As of this point in the development it is recommended to work inside of a
`Python` [virtual environment](https://docs.python.org/3/library/venv.html)

To install the required packages run
```sh
pip install -r requirements.txt
```

To use the wrappers you must have the `sgtsnepi` library installed locally on your system. 
You can find the [source code](https://github.com/fcdimitr/sgtsnepi/tree/julia-python-packages)
in the original repository where I am using the `julia-python-packages` branch.

## Running the Demo
from the source directory run
```
python -m tests.demo mm_file.mtx
```
where `mm_file.mtx` is a file containing the input matrix which is in the
[Matrix Market](https://math.nist.gov/MatrixMarket/index.html) file format

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
