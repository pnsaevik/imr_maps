from setuptools import setup, find_namespace_packages


def get_gdal_version():
    import subprocess
    from subprocess import PIPE
    import re
    try:
        retval = subprocess.run(['gdalinfo', '--version'], stdout=PIPE)
    except FileNotFoundError:
        raise FileNotFoundError('GDAL not found on path. Please install GDAL.')
    text = retval.stdout.decode('utf8')
    version_match = re.match(r'.*?(\d*\.\d*\.\d*)', text)
    if version_match:
        version = version_match.group(1)
    else:
        raise FileNotFoundError('Unknown GDAL version found on path.')
    return version


setup(
    name='imr_farms',
    version='1.0.0',
    packages=find_namespace_packages(where='src'),
    package_dir={'': 'src'},
    # package_data={'imr.farms.data': ['*']},
    url='',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],
    author='Pål Næverlid Sævik',
    author_email='a5606@hi.no',
    description='Retrieve public data on Norwegian aquaculture locations',
    install_requires=[
        'numpy', 'pytest', 'GDAL==' + get_gdal_version(), 'xarray', 'netCDF4',
    ]
)
