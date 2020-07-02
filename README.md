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

## Usage: Farm locations

The package `imr.maps` provides the functions `farm_locations` and
`farm_areas`, both supplied with an optional `reload` parameter. They return
an `xarray` dataset, directly downloaded from
`https://ogc.fiskeridir.no/wfs.ashx`. The tables are cached locally (in
`.local/share`) as georeferenced netCDF files, and re-downloaded only when
the `reload` parameter is set to `True`.

Sample usage:

```python
from imr.maps import farm_locations

with farm_locations() as dset:
    print(dset)
```

## Usage: Fish spawning grounds

The package `imr.maps` provides the function `spawn_area` to download fish
spawning areas from the geoserver `https://maps.imr.no/geoserver/fisk/ows`.
The function can store the result as a GeoJSON file. There is no caching,
a function call always downloads the data.

Valid layer names include, for instance, `fisk:Kveite_bw`, `fisk:Sei_bw`,
`fisk:nvgsild_bw`, `fisk:makrell_bw`. All valid layer names can be
obtained by the WFS request 
`https://maps.imr.no/geoserver/fisk/ows?service=WFS&request=GetCapabilities`.

Sample usage:

```python
from imr.maps import spawn_area

layer_name = 'fisk:nvgsild_bw'
outfile = 'spawn.geojson'
spawn_area(layer_name, outfile)
``` 


## Usage: Coastlines

The package `imr.maps` provides the function `coastlines` to retrieve
high-resolution coastlines from a server. The result is cached, so the
download is only happening at the first function call. Optionally, a low-
resolution coastline can be retrieved as well.

The coastlines are clipped to a rectangular lat/lon area.


Sample usage:
```python
from imr.maps import coastlines

latlim = [60, 60.01]
lonlim = [5, 5.01]

c = coastlines(latlim, lonlim)
# For low-resolution, use coastlines(latlim, lonlim, 'gshhs')

print(c.latitude.values)
print(c.longitude.values)
print(c.patchsize.values)
```
