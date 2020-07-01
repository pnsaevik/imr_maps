def locations(reload=False):
    from imr.maps.wfs import resource
    import xarray as xr
    fname = resource('layer_262', 'fiskdir', reload)
    dset = xr.open_dataset(fname)
    return dset.assign_coords(record=dset.loknr.values)


def areas(reload=False):
    from imr.maps.wfs import resource
    import xarray as xr
    fname = resource('layer_203', 'fiskdir', reload)
    dset = xr.open_dataset(fname)
    loknr = [int(n.decode('utf8').split(' ')[0]) for n in dset.lokalitet.values]
    dset = dset.assign(loknr=xr.Variable('record', loknr))
    return dset.assign_coords(record=loknr)
