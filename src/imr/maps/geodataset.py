import xarray as xr
import numpy as np


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
        dset.coords[coords[0]].attrs[
            'standard_name'] = 'projection_x_coordinate'
        dset.coords[coords[0]].attrs['axis'] = 'X'
        dset.coords[coords[1]].attrs[
            'standard_name'] = 'projection_y_coordinate'
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
