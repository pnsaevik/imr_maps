from osgeo import ogr, gdal


def get_dataset():
    # Speeds up querying WFS capabilities for services with alot of layers
    gdal.SetConfigOption('OGR_WFS_LOAD_MULTIPLE_LAYER_DEFN', 'NO')

    # Set config for paging. Works on WFS 2.0 services and WFS 1.0 and 1.1 with some other services.
    gdal.SetConfigOption('OGR_WFS_PAGING_ALLOWED', 'YES')
    gdal.SetConfigOption('OGR_WFS_PAGE_SIZE', '10000')

    # Open the webservice
    url = 'https://ogc.fiskeridir.no/wfs.ashx'
    wfs_drv = ogr.GetDriverByName('WFS')
    wfs_ds = wfs_drv.Open('WFS:' + url)

    if not wfs_ds:
        raise IOError(f'Can not open WFS datasource: {url}')

    # Iterate over layers
    # layers = {}
    # for i in range(wfs_ds.GetLayerCount()):
    #    layer = wfs_ds.GetLayerByIndex(i)
    return wfs_ds.GetLayerCount()


def main():
    return get_dataset()
