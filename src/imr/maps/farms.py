from imr.maps.wfs import resource


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
