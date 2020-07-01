from setuptools import setup, find_namespace_packages


setup(
    name='imr_maps',
    version='0.3.0',
    packages=find_namespace_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'farmloc=imr.maps.farms:farmloc_script',
            'gyteomr=imr.maps.spawn:gyteomr_script',
        ],
    },
    # package_data={'imr.farms.data': ['*']},
    url='https://github.com/pnsaevik/imr_maps',
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        "Operating System :: OS Independent",
    ],
    author='Pål Næverlid Sævik',
    author_email='a5606@hi.no',
    description='Retrieve public data on Norwegian aquaculture locations',
    install_requires=[
        'numpy>=1.16', 'pytest', 'GDAL', 'xarray', 'netCDF4', 'PyYAML'
    ],
    python_requires='>=3.6',
)
