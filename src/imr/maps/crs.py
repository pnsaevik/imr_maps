from osgeo import osr


EPSG_CODES = dict(
    wgs84=4326,
    utm29n=32629,
    utm30n=32630,
    utm31n=32631,
    utm32n=32632,
    utm33n=32633,
    utm34n=32634,
    utm35n=32635,
    utm36n=32636,
    etrs89=4258,
    etrs89_utm29n=25829,
    etrs89_utm30n=25830,
    etrs89_utm31n=25831,
    etrs89_utm32n=25832,
    etrs89_utm33n=25833,
    etrs89_utm34n=25834,
    etrs89_utm35n=25835,
    etrs89_utm36n=25836,
)


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


def projection_from_epsg(epsg_code):
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(epsg_code)
    return proj
