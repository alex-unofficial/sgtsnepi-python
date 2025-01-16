import os
import sys
import shutil
import subprocess

from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.command.build import build


class CustomBuildExt(build_ext):
    def run(self):
        # Clone https://github.com/fcdimitr/sgtsnepi
        if not os.path.exists('libsgtsnepi'):
            subprocess.check_call([
                'git', 'clone',
                '--branch', 'julia-python-packages',
                '--depth', '1',
                'https://github.com/alex-unofficial/sgtsnepi',
                'libsgtsnepi'
            ])

        # Build the sgtsnepi library
        os.chdir('libsgtsnepi')
        subprocess.check_call(
            ['meson', 'setup', '--reconfigure', 'build',     '-Dfftw_parallel_lib=none',],
            env=os.environ.copy()
        )
        subprocess.check_call(
            ['meson', 'compile', '-C', 'build'],
            env=os.environ.copy()
        )
        os.chdir('..')
        # Determine the shared library file name by platform
        if sys.platform.startswith('linux'):
            lib_file = 'libsgtsnepi.so.0'
        elif sys.platform == 'darwin':
            lib_file = 'libsgtsnepi.0.dylib'
        elif os.name == 'nt':
            lib_file = 'libsgtsnepi.dll'
        else:
            # fallback, or raise an error if unrecognized
            raise RuntimeError(f"Unsupported platform: {sys.platform}")
        
        # Copy the compiled shared library into package dir
        os.makedirs(os.path.join(self.build_lib, 'sgtsnepi', 'lib'), exist_ok=True)
        shutil.copy(
            os.path.join('libsgtsnepi', 'build', lib_file),
            os.path.join(self.build_lib, 'sgtsnepi', 'lib')
        )
        # Continue with the standard build_ext steps
        super().run()

class CustomBuild(build):
    def run(self):
        # Include build_ext as part of the build process
        self.run_command('build_ext')

        # Continue with the standard build steps
        super().run()


setup(
    cmdclass={
        'build_ext': CustomBuildExt,
        'build': CustomBuild,
    }
)
