def area(layer_name, outfile=None, wms_codes=(10,)):
    from .wfs import get_wfs
    wfs_server = 'https://maps.imr.no/geoserver/fisk/ows'
    wfs_ds = get_wfs(wfs_server)
    wfs_layer = wfs_ds.GetLayerByName(layer_name)

    from osgeo import ogr
    memdriver = ogr.GetDriverByName('MEMORY')
    ds = memdriver.CreateDataSource('gyte')
    layer = ds.CopyLayer(wfs_layer, layer_name)

    # Filter out features
    for fid in range(1, layer.GetFeatureCount() + 1):
        feature = layer.GetFeature(fid)
        wms_code = next(
            feature.GetField(i)
            for i in range(feature.GetFieldCount())
            if feature.GetFieldDefnRef(i).GetName() == 'wms_code'
        )
        if wms_code not in wms_codes:
            layer.DeleteFeature(fid)

    if outfile:
        jsondriver = ogr.GetDriverByName('GeoJSON')
        out = jsondriver.CreateDataSource(outfile)
        out.CopyLayer(layer, layer_name)
        del out

    return ds
