servers = {
    'fiskdir': 'https://gis.fiskeridir.no/server/services/FiskeridirWFS/MapServer/WFSServer',
    'imr_fisk': 'https://kart.hi.no/data/ows',
}


def get_wfs(url):
    from osgeo import ogr, gdal
    gdal.UseExceptions()
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
    return os.path.join(writable_dir, 'imr_maps')


def download_wfs_layer(layer, url, outfile):
    import subprocess
    import logging
    logging.getLogger(__name__).info(f'Downloading {layer} from {url}')
    cmd = ['ogr2ogr', '-f', 'netCDF', f'{outfile}', f'WFS:{url}', f'{layer}']
    subprocess.run(cmd)


def resource(layer, server, recompute=False, expires=None):
    from pathlib import Path

    def get_key(*strs):
        from hashlib import sha256
        hasher = sha256()
        hasher.update("".join(strs).encode('utf-8'))
        return hasher.digest().hex()

    key = get_key(server, layer)
    cachedir = Path(writable_location())
    cachedir.mkdir(parents=True, exist_ok=True)
    outfile = cachedir.joinpath(key)

    if recompute:
        do_download = True
    else:
        if not outfile.exists():
            do_download = True
        else:
            if expires is None:
                do_download = False
            else:
                import os
                import time
                elapsed = time.time() - os.path.getmtime(outfile)
                do_download = (elapsed > expires)

    if do_download:
        url = servers[server]
        download_wfs_layer(layer, url, outfile)

    if not outfile.exists():
        raise IOError(f'Unable to download resource {layer} from {server}')

    return outfile
