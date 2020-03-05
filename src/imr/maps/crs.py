from osgeo import osr


def projection_from_dataset(dset):
    potential_projections = [(k, v) for k, v in dset.data_vars.items()
                             if v.shape == () and 'spatial_ref' in v.attrs]
    
    if len(potential_projections) == 0:
        raise ValueError("No projection found in dataset")

    # Use the spatial_ref attribute if present
    wkt = potential_projections[0][1].spatial_ref
    proj = osr.SpatialReference()
    proj.ImportFromWkt(wkt)
    return proj
