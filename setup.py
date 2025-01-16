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
                '--branch', 'debug',
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
       # Figure out the name produced by Meson
        if sys.platform.startswith('darwin'):
            built_lib_name = 'libsgtsnepi.0.dylib'
            final_lib_name = 'libsgtsnepi.so.0'   # unify the name to .so.0
        elif sys.platform.startswith('linux'):
            built_lib_name = 'libsgtsnepi.so.0'
            final_lib_name = 'libsgtsnepi.so.0'
        else:
            raise RuntimeError(f"Unsupported platform: {sys.platform}")

        # Copy from what was built to our final uniform name
        build_lib_dir = os.path.join('libsgtsnepi', 'build')
        os.makedirs(os.path.join(self.build_lib, 'sgtsnepi', 'lib'), exist_ok=True)

        # If needed, rename or copy
        shutil.copy(
            os.path.join(build_lib_dir, built_lib_name),
            os.path.join(self.build_lib, 'sgtsnepi', 'lib', final_lib_name)
        )

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
