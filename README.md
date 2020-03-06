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

The package `imr.maps` provides two classes, `SpatialReference` which
represents a geospatial reference frame, and `GeoDataset` which represents
a CF-compliant netCDF dataset with geospatial information.

Sample usage:

```python
from imr.maps import SpatialReference, GeoDataset
import xarray as xr

wgs84 = SpatialReference.from_epsg(4326)
utm33n = SpatialReference.from_epsg(32633)
x, y = [10000], [6710000]
lon, lat = SpatialReference.transform(x, y, utm33n, wgs84)


dset = GeoDataset(
    data_vars=dict(
        mydata=xr.Variable(
            dims=('y', 'x'), 
            data=[[1, 2, 3], [4, 5, 6]],
        ),
    ),
    coords=dict(
        x=[0, 10000, 20000],
        y=[6700000, 6710000],    
    ),
)

dset = dset.create_grid_mapping(utm33n)
dset = dset.create_geocoords(["x", "y"])
dset.to_netcdf('out.nc')
```
