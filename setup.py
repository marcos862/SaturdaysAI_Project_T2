import os.path
import sys
from distutils import log

from setuptools import setup
from setuptools.command.develop import develop as _develop
from setuptools.command.install import install as _install

version_file = os.path.join(
            os.path.dirname(__file__),
            "_version.py")
exec(open(version_file).read())

package_name = "School_Drop_Detector"

# build package_dir first

class CInstallWrapper(object):
    """Encapsulate pre/post install actions, so that it could be easily reused
    in editable (develop) mode
    """
    def Pre(self):
        """Pre-install action should be inserted here"""
        sMessage = "Pre install actions go here"
        log.info(sMessage)

    def Post(self):
        """Post-install action should be inserted here"""
        sMessage = "Post install actions go here"

        log.info(sMessage)

    def _ExecuteShellCommand(self, sCommand):
        import subprocess
        p = subprocess.Popen(sCommand,
            shell=True,
            stderr=subprocess.PIPE,
        )
        _sStdOut, sStdErr = p.communicate()
        p.wait()

        if sStdErr:
            log.error('''can't execute command "{sCommand}" ({sStdErr})'''.format(
                sCommand=sCommand,
                sStdErr = sStdErr,
            ))
# end class CInstallWrapper


class develop(_develop):
    def run(self):
        if any([
            '--uninstall' in sys.argv,
            '-u'          in sys.argv,
        ]):
            _develop.run(self)      

        else:
            iw = CInstallWrapper()

            iw.Pre()
            _develop.run(self)      
            iw.Post()
# end class develop


class install(_install):
    def run(self):
        iw = CInstallWrapper()

        iw.Pre()
        _install.run(self)      
        iw.Post()
# end class install

setup(
    name=package_name,
    version=str(__version__),
    description='School Drop Detector using ML (Random Forest)',
    long_description=open('README.md').read(),
    author='Marcos Bolanos, Angel Cruz, Griselda Perez, Xochitl Arroyo',
    author_email='marcos.ibolanos@gmail.com',
    url='https://github.com/marcos862/SaturdaysAI_Project_T2', 

    packages=['Model', 'Utils'],

    cmdclass={
        'develop': develop,
        'install': install,
    },

    include_package_data=True,
    install_requires=[
        'pandas==0.25.3',
        'seaborn==0.9.0',
        'matplotlib==3.1.1',
        'scikit-learn==0.21.2',
        'numpy==1.16.4',
        'imbalanced-learn==0.5.0',
    ],
    extras_require={
    },
    namespace_packages=[
    ],
)
