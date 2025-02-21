# A list of the Python sources that should appear next to the extension
python_files = [
  'sgtsne.py',
  '__init__.py'
]

# mark sources of a single module for an installation
py3.install_sources(
    python_files,
    pure: false, # Will be installed next to binaries
    subdir: 'sgtsnepi/',  # Folder relative to site-packages to install to
)

py3.extension_module(
    '_sgtsnepi',
    ['sgtsne_pybind.cpp'],
    include_directories: [],
    dependencies : [py3_dep, pybind11_dep, sgtsnepilib_dep],
    install: true,
    cpp_args: [],
    subdir: 'sgtsnepi/',
)