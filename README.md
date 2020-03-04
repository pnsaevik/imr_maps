[![Build Status](https://travis-ci.com/pnsaevik/imr_farms.png)](https://travis-ci.com/pnsaevik/imr_farms)

# imr.farms
Retrieve map data on Norwegian aquaculture locations

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

```pip install imr_farms```

## Usage

The package provides two functions, `imr.farms.locations()` and
`imr.farms.areas()`, supplied with an optional `recompute` parameter.
Both return an `xarray` dataset, directly downloaded from
https://ogc.fiskeridir.no/wfs.ashx . The tables are cached locally (in
`.local/share`) as georeferenced netCDF files, and re-downloaded only when the
`recompute` parameter is set to `True`.

Sample usage:

```python
from imr.farms import locations

with locations() as dset:
    print(dset)
```
