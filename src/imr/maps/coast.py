import contextlib


def download_source(files, server, user=None):
    # Default user
    if user is None:
        import getpass
        user = getpass.getuser()

    # Create output location
    from imr.maps.wfs import writable_location
    from uuid import uuid4
    from pathlib import Path
    tmpdir = Path(writable_location()).joinpath(uuid4().hex + uuid4().hex)
    tmpdir.mkdir(parents=True, exist_ok=True)

    # Fetch data
    import subprocess
    import logging
    cmd = ['scp', '-oBatchMode=yes', f"{user}@{server}:{files}", f"{tmpdir}"]
    logging.getLogger(__name__).info(' '.join([f'"{s}"' for s in cmd]))
    subprocess.run(cmd)

    import os
    if len(os.listdir(tmpdir)) == 0:
        raise OSError('Download unsuccessful')

    return tmpdir


def cached_resource(name):
    # Define server location
    server = 'dedun.imr.no'
    prefix = '/data/osea/a5606/hosting/coast/'
    patterns = dict(
        kartverket='landomr4.*',
        gshhs='GSHHS_f_L1.*'
    )

    # Define caching location
    from pathlib import Path
    from imr.maps.wfs import writable_location
    coast_dir = Path(writable_location()).joinpath('coast')
    coast_dir.mkdir(parents=True, exist_ok=True)
    resource_dir = coast_dir.joinpath(name)

    # Download if necessary
    if not resource_dir.is_dir():
        import shutil
        tmpdir = download_source(prefix + patterns[name], server)
        shutil.move(tmpdir, resource_dir)

    if not resource_dir.is_dir():
        raise OSError('Cannot obtain resources')

    return resource_dir


@contextlib.contextmanager
def clip_layer(local_file, latlim, lonlim):

    # Check if the input is a shapefile folder
    from pathlib import Path
    localpath = Path(local_file)
    if localpath.is_dir():
        files_within = list(localpath.glob('*'))
        shapefile_within = list(localpath.glob('*.shp'))
        if shapefile_within:
            localpath = shapefile_within[0]
        else:
            localpath = files_within[0]

    # Create output shapefile folder
    import subprocess
    import shlex
    from uuid import uuid4
    import os
    outdir = 'clip_layer_' + uuid4().hex + uuid4().hex
    os.mkdir(outdir)

    try:
        outfile = Path(outdir).joinpath('clip_layer.shp')
        spatlim = f'{lonlim[0]} {latlim[0]} {lonlim[1]} {latlim[1]}'
        cmd = (f'ogr2ogr -spat {spatlim} -clipsrc spat_extent '
               f'"{outfile}" "{localpath}"')
        subprocess.run(shlex.split(cmd), capture_output=True)

        yield outdir
    finally:
        for f in os.listdir(outdir):
            try:
                os.unlink(os.path.join(outdir, f))
            except OSError:
                pass
        try:
            os.rmdir(outdir)
        except OSError:
            pass


def merged_areas(shapefolder):
    # Find shapefile
    from pathlib import Path
    p = Path(shapefolder)
    shapefile = str(list(p.glob('*.shp'))[0])

    # Load shapefile
    from osgeo import ogr
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shapefile, 0)
    layer = dataSource.GetLayer()

    # Extract polygons
    from shapely import wkb
    from shapely import geometry
    polys = []
    for feature in layer:
        geom = wkb.loads(feature.GetGeometryRef().ExportToWkb())
        if isinstance(geom, geometry.Polygon):
            polys.append(geom)
        else:
            polys += list(geom)

    # Combine intersecting polygons
    from shapely import ops
    uni = ops.cascaded_union(polys)
    if isinstance(uni, geometry.Polygon):
        uni = geometry.MultiPolygon([uni])

    # Extract coordinates
    import numpy as np
    coords = [np.array(g.exterior.coords.xy).T for g in uni]
    coords_len = [len(c) for c in coords]
    if coords:
        coords_concat = np.concatenate(coords)
    else:
        coords_concat = np.empty((0, 2), dtype=float)

    # Create xarray with metadata
    import xarray as xr
    return xr.Dataset({
        'latitude': xr.DataArray(
            coords_concat[:, 1],
            dims='node_num',
            name='latitude',
            attrs=dict(
                standard_name='latitude',
                units='degrees_north',
            ),
        ),

        'longitude': xr.DataArray(
            coords_concat[:, 0],
            dims='node_num',
            name='longitude',
            attrs=dict(
                standard_name='longitude',
                units='degrees_east',
            ),
        ),

        'patchsize': xr.DataArray(
            coords_len,
            dims='patch_num',
            name='patchsize',
            attrs=dict(
                sample_dimension='node_num',
            ),
        ),
    })


def coastlines(latlim, lonlim, source='kartverket'):
    """
    Retrieve a rectangular lat/lon section of coastlines.

    :param latlim: A two-element list of latitude limits
    :param lonlim: A two-element list of longitude limits
    :param source: Either 'kartverket' (high-resolution) or 'gshhs' (low-resolution)
    :return: An xarray dataset with variables 'latitude', 'longitude',
    'patchsize', where 'latitude', 'longitude' are the land patch coordinates
    and 'patchsize' is the number of coordinates per land patch.
    """
    data = cached_resource(source)  # Download data
    with clip_layer(data, latlim, lonlim) as clip_data:  # Clip data to area
        return merged_areas(clip_data)  # Merge disjoint land areas
