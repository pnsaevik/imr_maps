from osgeo import ogr, gdal


URL = 'https://ogc.fiskeridir.no/wfs.ashx'


def get_wfs(url):
    # Speeds up querying WFS capabilities for services with alot of layers
    gdal.SetConfigOption('OGR_WFS_LOAD_MULTIPLE_LAYER_DEFN', 'NO')

    # Set config for paging. Works on WFS 2.0 services and WFS 1.0 and 1.1 with some other services.
    gdal.SetConfigOption('OGR_WFS_PAGING_ALLOWED', 'YES')
    gdal.SetConfigOption('OGR_WFS_PAGE_SIZE', '10000')

    # Open the webservice
    wfs_drv = ogr.GetDriverByName('WFS')
    wfs_ds = wfs_drv.Open('WFS:' + url)
    if not wfs_ds:
        raise IOError(f'Can not open WFS datasource: {url}')
    return wfs_ds


def get_layer(title, wfs_ds):
    # Iterate over layers
    for i in range(wfs_ds.GetLayerCount()):
        layer = wfs_ds.GetLayerByIndex(i)
        if title == layer.GetMetadataItem('TITLE'):
            return layer.GetDescription()

    return None


def writable_location():
    # for the writable data directory (i.e. the one where new data goes), follow
    # the XDG guidelines found at
    # https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
    import os
    writable_dir_std = os.path.join(os.path.expanduser('~'), '.local', 'share')
    writable_dir = os.environ.get("XDG_DATA_HOME", writable_dir_std)
    return os.path.join(writable_dir, 'imr_farms')
