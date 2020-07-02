from osgeo.osr import SpatialReference, CoordinateTransformation
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


def crs_from_wkt(wkt):
    """Create SpatialReference from Well Known Text (WKT)

    :param wkt:
        WKT representation of the spatial reference frame
    :type wkt: str
    :returns:
        SpatialReference object
    :rtype: SpatialReference
    """
    proj = SpatialReference()
    proj.ImportFromWkt(wkt)
    return proj


def crs_from_epsg(epsg):
    """Create SpatialReference from EPSG code

    :param epsg:
        EPSG code representing of the spatial reference frame
    :type epsg: int
    :returns:
        SpatialReference object
    :rtype: SpatialReference
    """
    proj = SpatialReference()
    proj.ImportFromEPSG(epsg)
    return proj


def crs_from_proj4str(proj4str):
    """Create SpatialReference from PROJ4 string

    :param proj4str:
        EPSG code representing of the spatial reference frame
    :type proj4str: str
    :returns:
        SpatialReference object
    :rtype: SpatialReference
    """
    proj = SpatialReference()
    proj.ImportFromProj4(proj4str)
    return proj


def crs_local(lon, lat):
    """Create local metric coordinate system based on ETRS89 and transverse
    mercator.

    :param lon:
        Longitude of the central location
    :param lat:
        Latitude of the central location
    :returns:
        SpatialReference object
    :rtype: SpatialReference
    """
    wkt = f"""
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
            PARAMETER["latitude_of_origin", {lat}],
            PARAMETER["central_meridian", {lon}],
            PARAMETER["scale_factor",1.0],
            PARAMETER["false_easting",0],
            PARAMETER["false_northing",0],
            AXIS["Easting",EAST],
            AXIS["Northing",NORTH]]
            """

    sr = SpatialReference()
    sr.ImportFromWkt(wkt)
    return sr


def crs_nf160(named_area, metric_unit=False):
    """Create coordinate system based on the NorFjords160 (NF160) grid

    :param named_area:
        Either of {'A01', 'A02', ..., 'A13'}
    :type named_area: str
    :param metric_unit:
        True if the coordinate system unit should be meters, False if the
        unit should be cells.
    :type metric_unit: bool
    :returns:
        SpatialReference object
    :rtype: SpatialReference
    """
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
    return _nor_roms(*params[named_area], metric_unit=metric_unit)


def crs_nk800(metric_unit=False):
    """Create coordinate system based on the NorKyst800 (NK800) grid

    :param metric_unit:
        True if the coordinate system unit should be meters, False if the
        unit should be cells.
    :type metric_unit: bool
    :returns:
        SpatialReference object
    :rtype: SpatialReference
    """
    return _nor_roms(metric_unit=metric_unit)


def crs_transform(x, y, from_crs, to_crs):
    """Transform coordinate values between two coordinate systems

    Transform coordinate values between two coordinate systems. The shape
    of the input arrays are preserved.

    :param x:
        First coordinate array
    :type: numpy.ndarray
    :param y:
        Second coordinate array
    :type: numpy.ndarray
    :param from_crs:
        Source coordinates reference frame
    :type from_crs: osgeo.osr.SpatialReference
    :param to_crs:
        Transformed coordinates reference frame
    :type to_crs: osgeo.osr.SpatialReference
    :returns:
        (xp, yp), the transformed coordinates
    :rtype: (numpy.ndarray, numpy.ndarray)
    """

    xarr = np.array(x)
    yarr = np.array(y)

    if len(xarr) == 0 and len(yarr) == 0:
        return np.array([x, y])

    ct = CoordinateTransformation(from_crs, to_crs)

    xrv = xarr.ravel()
    yrv = yarr.ravel()
    points = np.stack([xrv, yrv, np.zeros_like(xrv)]).T
    result = np.array(ct.TransformPoints(points))
    xp = result[:, 0].reshape(xarr.shape)
    yp = result[:, 1].reshape(yarr.shape)
    return xp, yp


def crs_to_gridmapping(crs):
    """Create grid_mapping variable from projection"""
    wkt = crs.ExportToWkt()
    dproj = xr.DataArray(
        dims=(), data=np.int8(0),
        attrs=dict(
            long_name="CRS definition",
            crs_wkt=wkt,
            spatial_ref=wkt,
            semi_major_axis=crs.GetSemiMajor(),
            inverse_flattening=crs.GetInvFlattening(),
            projected_crs_name=crs.GetAttrValue('PROJCS'),
            geographic_crs_name=crs.GetAttrValue('GEOGCS'),
            horizontal_datum_name=crs.GetAttrValue('DATUM'),
            reference_ellipsoid_name=crs.GetAttrValue('SPHEROID'),
            prime_meridian_name=crs.GetAttrValue('PRIMEM'),
            towgs84=crs.GetTOWGS84(),
        ),
    )

    proj_name = crs.GetAttrValue('PROJECTION', 0)

    # If WGS84 or ETRS89
    if proj_name is None:
        dproj.attrs['grid_mapping_name'] = 'latitude_longitude'

    # If transverse mercator
    elif proj_name == "Transverse_Mercator":
        dproj.attrs['grid_mapping_name'] = 'transverse_mercator'
        dproj.attrs['scale_factor_at_central_meridian'] = crs.GetProjParm(
            'scale_factor')
        dproj.attrs['longitude_of_central_meridian'] = crs.GetProjParm(
            'central_meridian')
        dproj.attrs['latitude_of_projection_origin'] = crs.GetProjParm(
            'latitude_of_origin')
        dproj.attrs['false_easting'] = crs.GetProjParm('false_easting')
        dproj.attrs['false_northing'] = crs.GetProjParm('false_northing')

    else:
        raise ValueError(f'Unknown projection: {proj_name}')

    return dproj


def crs_from_gridmapping(grid_mapping):
    """Create projection from grid_mapping variable"""
    if 'crs_wkt' not in grid_mapping.attrs:
        raise NotImplementedError('At present, a "crs_wkt" attr is required')

    wkt = grid_mapping.attrs['crs_wkt']
    sr = SpatialReference()
    sr.ImportFromWkt(wkt)
    return sr


def _nor_roms(xp=3991, yp=2230, dx=800, ylon=70, name='NK800', metric_unit=False):
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

    sr = SpatialReference()
    sr.ImportFromWkt(wkt)
    return sr


def set_crs(dset: xr.Dataset, crs, coords=None, data_vars=None):
    grid_mapping, _ = _load_crs(dset, crs)
    dset = dset.assign({grid_mapping.name: grid_mapping})

    if coords is not None:
        dset = _add_geoattrs_to_coords(dset, grid_mapping, coords)

    if data_vars is not None:
        dset = dset.copy()
        for v in data_vars:
            dset.data_vars[v].attrs['grid_mapping'] = grid_mapping.name

    return dset


def _load_crs(dset, gridmapping_or_crs):
    if isinstance(gridmapping_or_crs, str):
        grid_mapping = dset.data_vars[gridmapping_or_crs]
        crs = crs_from_gridmapping(grid_mapping)
    elif isinstance(gridmapping_or_crs, xr.DataArray):
        grid_mapping = gridmapping_or_crs
        crs = crs_from_gridmapping(grid_mapping)
    else:
        grid_mapping_varname = 'crs_def'
        grid_mapping = crs_to_gridmapping(gridmapping_or_crs)
        grid_mapping.name = grid_mapping_varname
        crs = gridmapping_or_crs

    return grid_mapping, crs


def change_crs(dset: xr.Dataset, old_coords, old_crs, new_coords, new_crs):
    dset = dset.copy()

    # Load coordinates
    old_x = dset.variables[old_coords[0]].values
    old_y = dset.variables[old_coords[1]].values
    if len(old_x.shape) == 1 and len(old_y.shape) == 1:
        old_x, old_y = np.meshgrid(old_x, old_y)

    # Find old dimensions
    xdims = dset.variables[old_coords[0]].dims
    ydims = dset.variables[old_coords[1]].dims
    if len(xdims) == 2:
        dims = xdims
    else:
        dims = ydims + xdims

    # Transform coordinates
    old_gridmap, old_proj = _load_crs(dset, old_crs)
    new_gridmap, new_proj = _load_crs(dset, new_crs)
    new_x, new_y = crs_transform(old_x, old_y, old_proj, new_proj)

    # Remove old grid mapping and coordinates
    dset = dset.drop_vars(old_gridmap.name)
    dset = dset.drop_vars(old_coords)

    # Check if new coordinates are one-dimensional
    xdiff = np.max(np.abs(np.diff(new_x, axis=0)))
    ydiff = np.max(np.abs(np.diff(new_y, axis=1)))
    if xdiff < 1e-8 and ydiff < 1e-8:
        # If one-dimensional, store as one-dimensional variables and
        # change dimension names to match coordinates
        dset = dset.assign_coords({
            new_coords[0]: xr.Variable(dims[1], new_x[0, :]),
            new_coords[1]: xr.Variable(dims[0], new_y[:, 0]),
        })  # type: xr.Dataset
        dset = dset.swap_dims(dict(zip(reversed(dims), new_coords)))
    else:
        # If two-dimensional, store as auxillary coordinates with the same
        # dimension names as the old coordinates
        dset = dset.assign_coords({
            new_coords[0]: xr.Variable(dims, new_x),
            new_coords[1]: xr.Variable(dims, new_y),
        })  # type: xr.Dataset

    # Find data vars referring to old coordinates
    old_data_vars = [k for k, v in dset.data_vars.items()
                     if 'grid_mapping' in v.attrs]

    # Add grid mapping to new dataset
    dset = set_crs(dset=dset, crs=new_gridmap, coords=new_coords,
                   data_vars=old_data_vars)

    return dset


def _add_geoattrs_to_coords(dset, grid_mapping, coords):
    grid_mapping_name = grid_mapping.attrs['grid_mapping_name']
    dset = dset.copy()

    dset.coords[coords[0]].attrs['axis'] = 'X'
    dset.coords[coords[1]].attrs['axis'] = 'Y'

    # If WGS84 or ETRS89
    if grid_mapping_name == 'latitude_longitude':
        dset.coords[coords[0]].attrs['standard_name'] = 'longitude'
        dset.coords[coords[1]].attrs['standard_name'] = 'latitude'

    # If rotated pole
    elif grid_mapping_name == 'rotated_latitude_longitude':
        dset.coords[coords[0]].attrs['standard_name'] = 'grid_longitude'
        dset.coords[coords[1]].attrs['standard_name'] = 'grid_latitude'

    # All other
    else:
        dset.coords[coords[0]].attrs['standard_name'] = 'projection_x_coordinate'
        dset.coords[coords[1]].attrs['standard_name'] = 'projection_y_coordinate'

    return dset
