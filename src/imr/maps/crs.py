from osgeo import osr
import numpy as np
import xarray as xr


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
    potential_projections = [v for v in dset.data_vars.values()
                             if 'grid_mapping_name' in v.attrs]
    
    if len(potential_projections) == 0:
        raise ValueError("No projection found in dataset")

    return projection_from_grid_mapping(potential_projections[0])


def projection_from_grid_mapping(grid_mapping):
    # Use the spatial_ref attribute if present
    wkt = grid_mapping.crs_wkt
    proj = osr.SpatialReference()
    proj.ImportFromWkt(wkt)
    return proj


def projection_from_epsg(epsg_code):
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(epsg_code)
    return proj


def projection_local(lon, lat):
    wkt = """
        PROJCS["Local ETRS89",
            GEOGCS["ETRS89",
                DATUM["European_Terrestrial_Reference_System_1989",
                    SPHEROID["GRS 1980",6378137,298.257222101,
                        AUTHORITY["EPSG","7019"]],
                    AUTHORITY["EPSG","6258"]],
                PRIMEM["Greenwich",0,
                    AUTHORITY["EPSG","8901"]],
                UNIT["degree",0.01745329251994328,
                    AUTHORITY["EPSG","9122"]],
                AUTHORITY["EPSG","4258"]],
            UNIT["metre",1,
                AUTHORITY["EPSG","9001"]],
            PROJECTION["Transverse_Mercator"],
            PARAMETER["latitude_of_origin",""" + str(lat) + """],
            PARAMETER["central_meridian",""" + str(lon) + """],
            PARAMETER["scale_factor",1.0],
            PARAMETER["false_easting",0],
            PARAMETER["false_northing",0],
            AXIS["Easting",EAST],
            AXIS["Northing",NORTH]]
            """

    ref = osr.SpatialReference()
    ref.ImportFromWkt(wkt)
    return ref


def projection_nf160(named_area, metric_unit=False):
    params = {
        'A01': (18704, 10752, 160, 70, 'NF160_A01'),
        'A02': (19254, 10352, 160, 70, 'NF160_A02'),
        'A03': (19254, 9282, 160, 70, 'NF160_A03'),
        'A04': (18854, 8992, 160, 70, 'NF160_A04'),
        'A05': (18104, 8922, 160, 70, 'NF160_A05'),
        'A06': (16904, 8582, 160, 70, 'NF160_A06'),
        'A07': (16074, 9082, 160, 70, 'NF160_A07'),
        'A08': (14804, 8932, 160, 70, 'NF160_A08'),
        'A09': (14054, 8932, 160, 70, 'NF160_A09'),
        'A10': (12954, 8802, 160, 70, 'NF160_A10'),
        'A11': (11554, 8952, 160, 70, 'NF160_A11'),
        'A12': (10004, 9422, 160, 70, 'NF160_A12'),
        'A13': (8754, 10552, 160, 70, 'NF160_A13'),
    }

    return projection_nk800(*params[named_area], metric_unit=metric_unit)


def projection_nk800(xp=3991, yp=2230, dx=800, ylon=70, name='NK800', metric_unit=False):
    if metric_unit:
        unit_str = 'UNIT["metre",1,AUTHORITY["EPSG","9001"]]'
        dx_unit = dx
    else:
        unit_str = f'UNIT["Cells",{dx}]]'
        dx_unit = 1

    wkt = f"""PROJCS["{name}",
        GEOGCS["ETRS89",
            DATUM["European_Terrestrial_Reference_System_1989",
                SPHEROID["GRS 1980",6378137,298.257222101,
                    AUTHORITY["EPSG","7019"]],
                AUTHORITY["EPSG","6258"]],
            PRIMEM["Greenwich",0,
                AUTHORITY["EPSG","8901"]],
            UNIT["degree",0.01745329251994328,
                AUTHORITY["EPSG","9122"]],
            AUTHORITY["EPSG","4258"]],
        PROJECTION["Polar_Stereographic"],
        PARAMETER["latitude_of_origin",60],
        PARAMETER["central_meridian",{ylon}],
        PARAMETER["scale_factor",1],
        PARAMETER["false_easting",{xp * dx_unit}],
        PARAMETER["false_northing",{yp * dx_unit}],
        {unit_str}"""

    ref = osr.SpatialReference()
    ref.ImportFromWkt(wkt)
    return ref


def transform(lon, lat, from_crs, to_crs):
    if len(lat) == 0 and len(lon) == 0:
        return np.array([lat, lon])

    ct = osr.CoordinateTransformation(from_crs, to_crs)

    points = np.array([lon, lat, np.zeros_like(lon)]).T
    return np.array(ct.TransformPoints(points)).T[:2]


def assign_crs(dset, **crs_kwargs):
    """Create grid_mapping variable from projection and assign to variable"""

    mapping = {key: grid_mapping_from_proj(key, proj)
               for key, proj in crs_kwargs.items()}
    return dset.assign(mapping)


def grid_mapping_from_proj(name, proj):
    """Create grid_mapping variable from projection"""
    wkt = proj.ExportToWkt()
    dproj = xr.DataArray(
        dims=(), data=np.int8(0), name=name,
        attrs=dict(
            long_name="CRS definition",
            crs_wkt=wkt,
            spatial_ref=wkt,
            semi_major_axis=proj.GetSemiMajor(),
            inverse_flattening=proj.GetInvFlattening(),
            projected_crs_name=proj.GetAttrValue('PROJCS'),
            geographic_crs_name=proj.GetAttrValue('GEOGCS'),
            horizontal_datum_name=proj.GetAttrValue('DATUM'),
            reference_ellipsoid_name=proj.GetAttrValue('SPHEROID'),
            prime_meridian_name=proj.GetAttrValue('PRIMEM'),
            towgs84=proj.GetTOWGS84(),
        ),
    )

    proj_name = proj.GetAttrValue('PROJECTION', 0)

    # If WGS84 or ETRS89
    if proj_name is None:
        dproj.attrs['grid_mapping_name'] = 'latitude_longitude'

    # If transverse mercator
    elif proj_name == "Transverse_Mercator":
        dproj.attrs['grid_mapping_name'] = 'transverse_mercator'
        dproj.attrs['scale_factor_at_central_meridian'] = proj.GetProjParm(
            'scale_factor')
        dproj.attrs['longitude_of_central_meridian'] = proj.GetProjParm(
            'central_meridian')
        dproj.attrs['latitude_of_projection_origin'] = proj.GetProjParm(
            'latitude_of_origin')
        dproj.attrs['false_easting'] = proj.GetProjParm('false_easting')
        dproj.attrs['false_northing'] = proj.GetProjParm('false_northing')

    else:
        raise ValueError(f'Unknown projection: {proj_name}')

    return dproj


def add_crs_to_dataset(dset, coords, proj):

    dset = assign_crs(dset, crs_def=proj)
    return add_geoattrs_to_coordinates(dset, dset['crs_def'], *coords)


def add_geoattrs_to_coordinates(dset, grid_mapping, *coords):
    """Convert existing dataset coordinates to geocoordinates
    
    Parameters
    ----------
    dset: xarray.Dataset
        The dataset to modify.
        
    grid_mapping: xarray.DataArray, xarray.Variable
        The grid_mapping entry containing crs definition.
        
    *coords: str
        Ordered list of coordinate names. In the case of latitude_longitude
        grid mapping, the correct order is ['lon', 'lat']. The coordinates must
        exist in the dataset.

    Returns
    -------
    A modified xarray.Dataset with crs info added to the specified coordinates.
    """

    grid_mapping_name = grid_mapping.attrs['grid_mapping_name']
    dset = dset.copy()

    # If WGS84 or ETRS89
    if grid_mapping_name == 'latitude_longitude':
        dset.coords[coords[0]].attrs['standard_name'] = 'longitude'
        dset.coords[coords[0]].attrs['units'] = 'degrees_east'
        dset.coords[coords[0]].attrs['axis'] = 'X'
        dset.coords[coords[1]].attrs['standard_name'] = 'latitude'
        dset.coords[coords[1]].attrs['units'] = 'degrees_north'
        dset.coords[coords[1]].attrs['axis'] = 'Y'

    # If transverse mercator
    elif grid_mapping_name == 'transverse_mercator':
        dset.coords[coords[0]].attrs['standard_name'] = 'projection_x_coordinate'
        dset.coords[coords[0]].attrs['axis'] = 'X'
        dset.coords[coords[1]].attrs['standard_name'] = 'projection_y_coordinate'
        dset.coords[coords[1]].attrs['axis'] = 'Y'

    else:
        raise ValueError(f'Unknown grid mapping: {grid_mapping_name}')

    # --- Add attributes to data vars ---

    for v in dset.data_vars:
        if all(c in dset[v].coords for c in coords):
            old_text = dset[v].attrs.get('grid_mapping', '')
            if old_text != '':
                old_text += ' '
            new_text = f'{grid_mapping.name}: {" ".join(coords)}'
            dset[v].attrs['grid_mapping'] = old_text + new_text

    # --- Add global attributes

    if 'Conventions' not in dset.attrs:
        dset.attrs['Conventions'] = 'CF-1.8'

    return dset
