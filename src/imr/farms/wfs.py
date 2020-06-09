from osgeo import ogr, gdal


servers = {
    'fiskdir': 'https://ogc.fiskeridir.no/wfs.ashx',
    'imr_fisk': 'http://maps.imr.no/geoserver/fisk/ows',
}


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


def download_wfs_layer(layer, url, outfile):
    import subprocess
    import logging
    logging.getLogger(__name__).info(f'Downloading {layer} from {url}')
    cmd = ['ogr2ogr', '-f', 'netCDF', f'{outfile}', f'WFS:{url}', f'{layer}']
    subprocess.run(cmd)


def resource(layer, server, recompute=False):
    from pathlib import Path

    outdir = Path(writable_location()).joinpath(server)
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir.joinpath(layer + '.nc')

    if recompute or not outfile.exists():
        url = servers[server]
        download_wfs_layer(layer, url, outfile)

    if not outfile.exists():
        raise IOError(f'Unable to download resource {layer} from {server}')

    return outfile


def locations(reload=False):
    import xarray as xr
    fname = resource('layer_262', 'fiskdir', reload)
    dset = xr.open_dataset(fname)
    return dset.assign_coords(record=dset.loknr.values)


def areas(reload=False):
    import xarray as xr
    fname = resource('layer_203', 'fiskdir', reload)
    dset = xr.open_dataset(fname)
    loknr = [int(n.decode('utf8').split(' ')[0]) for n in dset.lokalitet.values]
    dset = dset.assign(loknr=xr.Variable('record', loknr))
    return dset.assign_coords(record=loknr)


def gyte(layer_name, outfile=None, wms_codes=(10, )):

    wfs_ds = get_wfs(servers['imr_fisk'])
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


def farmloc_script():
    import sys

    args = sys.argv

    # Pop reload arg
    reload = "--reload" in args
    if reload:
        args = args.copy()
        del args[args.index("--reload")]

    if len(args) != 2:
        print("""
FARMLOC
   Find location (and more) for the specified farm
        
Usage:

farmloc [--reload] loknr

""")
        return

    try:
        loknr = int(args[1])
    except ValueError:
        print("Location number must be an integer")
        return

    try:
        loc = locations(reload).sel(record=loknr)
        ar = areas(reload).sel(record=loknr)
    except KeyError:
        print(f"Location {loknr} not found")
        return

    def decode(e):
        ee = e.values.item()
        if isinstance(ee, bytes):
            return ee.decode('utf8')
        return ee

    loc_dict = {v: decode(loc[v]) for v in loc.variables}
    ar_dict = {v: decode(ar[v]) for v in ar.variables}
    d = dict(location=loc_dict, area=ar_dict)

    import yaml
    print(yaml.dump(d, allow_unicode=True))


def gyteomr_script():
    import sys
    args = sys.argv

    layers = {
        "blålange": "fisk:Blaalange_bw",
        "blåkveite": "fisk:Blaakveite_bw",
        "brisling": "fisk:Brisling_bw",
        "brosme": "fisk:Brosme_bw_3",
        "hvitting": "fisk:Hvitting_bw",
        "hyse": "fisk:hyse_nea_bw",
        "kolmule": "fisk:kolmule_bw_1_1",
        "kveite": "fisk:Kveite_bw",
        "kysttorsk_nord": "fisk:kysttorsk_n_62g_bw",
        "kysttorsk_sør": "fisk:Kysttorsk_soer_for_62N_bw",
        "lange": "fisk:Lange_bw",
        "lodde": "fisk:lodde_bw",
        "lysing": "fisk:Lysing_bw",
        "makrell": "fisk:makrell_bw",
        "makrellstørje": "fisk:Makrellstorje_bw",
        "nordsjøhyse": "fisk:Nordsjohyse_bw",
        "nordsjøsei": "fisk:NordsjoSei_bw",
        "nordsjøsild": "fisk:Nordsjosild_bw3",
        "nordsjøtorsk": "fisk:Nordsjotorsk_bw",
        "polartorsk": "fisk:Polartorsk_bw2",
        "rognkjeks": "fisk:rognkjeks_rognkall_bw",
        "rødspette": "fisk:Roedspette_bw",
        "taggmakrell": "fisk:Taggmakrell_bw",
        "tobis": "fisk:Tobis_gyteomrade",
        "torsk_nea": "fisk:torsk_nea_bw",
        "sei": "fisk:Sei_bw",
        "sei_nea": "fisk:sei_nea_bw",
        "sild_nvg": "fisk:nvgsild_bw",
        "snabeluer": "fisk:snabeluer_bw2",
        "vanliguer": "fisk:Vanliguer_bw",
        "øyepål": "fisk:Oyepaal_bw",
    }

    def print_valid_species():
        print("Valid species include: ")
        for k, v in layers.items():
            print(f'  - {k} ({v})')

    # Pop wms_code arg
    try:
        idx = [arg.startswith('--wms_codes=') for arg in args].index(True)
        wmscode_str = args.pop(idx)
    except ValueError:
        wmscode_str = '--wms_codes=10'
    codes = tuple([int(s) for s in wmscode_str.split("=")[1].split(",")])

    if len(args) != 3:
        print("GYTEOMR")
        print("   Download spawning area to geojson file\n")
        print("Usage:\n")
        print('gyteomr [--wms_codes=code1,code2,...] "species" out.geojson\n')
        print('By default, only wms code 10 ("gyteområde") is included.\n')
        print_valid_species()
        return

    species = args[1].lower()
    if species not in layers:
        layer = species
    else:
        layer = layers[species]

    try:
        gyte(layer_name=layer, outfile=args[2], wms_codes=codes)
    except ValueError:
        print(f"Unknown species: {args[1]}\n")
        print_valid_species()
