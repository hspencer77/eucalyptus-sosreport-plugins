# Copyright 2015 Eucalyptus Systems, Inc.
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from distutils.command.build_py import build_py
from distutils.command.sdist import sdist
from setuptools import setup
import os.path
import sys
import subprocess

from sos.plugins.eucameta import __version__


class build_py_with_git_version(build_py):
    '''Like build_py, but also hardcoding the version in __init__.__version__
       so it's consistent even outside of the source tree'''

    def build_module(self, module, module_file, package):
        orig_outfile, _ = build_py.build_module(self, module, module_file,
                                                package)
        if module == 'eucameta' and package == 'sos.plugins':
            version_line = "__version__ = '{0}'\n".format(__version__)
            new_outfile = orig_outfile + '.new'
            with open(new_outfile, 'w') as new_fh:
                with open(orig_outfile) as orig_fh:
                    for line in orig_fh:
                        if line.startswith('__version__ ='):
                            new_fh.write(version_line)
                        else:
                            new_fh.write(line)
                new_fh.flush()
            os.rename(new_outfile, orig_outfile)

class sdist_with_git_version(sdist):
    '''Like sdist, but also hardcoding the version in __init__.__version__ so
       it's consistent even outside of the source tree'''

    def make_release_tree(self, base_dir, files):
        sdist.make_release_tree(self, base_dir, files)
        version_line = "__version__ = '{0}'\n".format(__version__)
        orig_module = os.path.join(base_dir, 'sos/plugins/eucameta.py')
        new_module = orig_module + '.new'
        with open(new_module, 'w') as new_fh:
            with open(orig_module) as orig_fh:
                for line in orig_fh:
                    if line.startswith('__version__ ='):
                        new_fh.write(version_line)
                    else:
                        new_fh.write(line)
            new_fh.flush()
        os.rename(new_module, orig_module)

setup(name='eucalyptus-sos-plugins',
      version=__version__,
      description='Eucalyptus SOS plugins',
      long_description='Eucalyptus SOS plugins',
      author="Eucalyptus Systems, Inc.",
      author_email="support@eucalyptus.com",
      url='https://github.com/eucalyptus/eucalyptus-sosreport-plugins/',
      packages=['sos.plugins', 'sos'],
      keywords = "sosreport eucalyptus sos-plugins",
      license='BSD (Simplified)',
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Plugins",
          "Intended Audience :: Customer Service",
          "Intended Audience :: System Administrators",
          "Operating System :: POSIX :: Linux",
          "License :: OSI Approved :: Simplified BSD License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet :: Log Analysis",
          "Topic :: Utilities"
      ],
      cmdclass={
          'build_py': build_py_with_git_version,
          'sdist': sdist_with_git_version
      },
      platforms='Posix')
