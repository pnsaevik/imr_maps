[![Build Status](https://travis-ci.com/pnsaevik/imr_maps.png)](https://travis-ci.com/pnsaevik/imr_maps)

# imr_maps
Utility functions for retrieving and handling map data.

## Dependencies

The package requires the python package GDAL, including its binary
dependencies. This package is most easily installed using `conda`,

```conda install GDAL```

On unix, GDAL can also be installed using
```
apt-add-repository ppa:ubuntugis/ppa
apt install gdal-bin libgdal-dev
pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==`gdal-config --version` 
```

## Installation

After the dependencies are installed, the package is installed using

```pip install imr_maps```

## Usage

The package `imr.farms` provides two functions, `locations()` and `areas()`,
supplied with an optional `reload` parameter. Both return an `xarray` dataset,
directly downloaded from https://ogc.fiskeridir.no/wfs.ashx . The tables are
cached locally (in `.local/share`) as georeferenced netCDF files, and
re-downloaded only when the `reload` parameter is set to `True`.

Sample usage:

```python
from imr.farms import locations

with locations() as dset:
    print(dset)
```

The package `imr.maps` provides methods and classes to work with georeferenced
netCDF files.
