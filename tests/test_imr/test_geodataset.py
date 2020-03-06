from imr.maps import GeoDataset
from imr.maps import SpatialReference
import xarray as xr
import pytest
import numpy as np


wgs84 = SpatialReference.from_epsg(4326)
utm33n = SpatialReference.from_epsg(32633)


@pytest.fixture(scope='module')
def dset():
    return GeoDataset(
        data_vars=dict(
            mydata=xr.Variable(
                dims=('band', 'lat', 'lon'),
                data=np.arange(2 * 3 * 4).reshape((2, 3, 4)),
            ),
        ),
        coords=dict(
            lat=[59, 60, 61],
            lon=[4, 5, 6, 7],
        ),
    )


class Test_create_grid_mapping:
    def test_add_crsdef_when_wgs84(self, dset):
        new_dset = dset.create_grid_mapping(wgs84)
        assert isinstance(dset, GeoDataset)
        assert set(new_dset.crs_def.attrs.keys()) == {
            'crs_wkt',
            'geographic_crs_name',
            'grid_mapping_name',
            'horizontal_datum_name',
            'inverse_flattening',
            'long_name',
            'prime_meridian_name',
            'projected_crs_name',
            'reference_ellipsoid_name',
            'semi_major_axis',
            'spatial_ref',
            'towgs84'
         }


class Test_create_geocoords:
    def test_add_coordattr_when_wgs84(self, dset):
        new_dset = dset.create_grid_mapping(wgs84)
        new_dset = new_dset.create_geocoords(['lon', 'lat'])
        assert set(new_dset.lat.attrs.keys()) == {
            'standard_name', 'units', 'axis'}
        assert set(new_dset.lon.attrs.keys()) == {
            'standard_name', 'units', 'axis'}

    def test_add_gridmappings_when_wgs84(self, dset):
        new_dset = dset.create_grid_mapping(wgs84)
        new_dset = new_dset.create_geocoords(['lon', 'lat'])
        assert set(new_dset.mydata.attrs.keys()) == {'grid_mapping'}

    def test_add_globals_when_wgs84(self, dset):
        new_dset = dset.create_grid_mapping(wgs84)
        new_dset = new_dset.create_geocoords(['lon', 'lat'])
        assert set(new_dset.attrs.keys()) == {'Conventions'}

    @pytest.fixture(scope='class')
    def dset2(self):
        return GeoDataset(
            data_vars=dict(
                mydata=xr.Variable(
                    dims=('band', 'y', 'x'),
                    data=np.arange(2 * 3 * 4).reshape((2, 3, 4)),
                ),
            ),
            coords=dict(
                y=[6700000, 6710000, 6720000],
                x=[0, 10000, 20000, 30000],
            ),
        )

    def test_add_crsdef_when_utm33n(self, dset2):
        new_dset = dset2.create_grid_mapping(utm33n)
        new_dset = new_dset.create_geocoords(['x', 'y'])
        assert set(new_dset.crs_def.attrs.keys()) == {
            'false_easting',
            'false_northing',
            'latitude_of_projection_origin',
            'longitude_of_central_meridian',
            'scale_factor_at_central_meridian',
            'crs_wkt',
            'geographic_crs_name',
            'grid_mapping_name',
            'horizontal_datum_name',
            'inverse_flattening',
            'long_name',
            'prime_meridian_name',
            'projected_crs_name',
            'reference_ellipsoid_name',
            'semi_major_axis',
            'spatial_ref',
            'towgs84'
        }

    def test_add_coordattr_when_utm33n(self, dset2):
        new_dset = dset2.create_grid_mapping(utm33n)
        new_dset = new_dset.create_geocoords(['x', 'y'])
        assert set(new_dset.x.attrs.keys()) == {
            'standard_name', 'axis'}
        assert set(new_dset.y.attrs.keys()) == {
            'standard_name', 'axis'}

    @pytest.fixture(scope='class')
    def dset3(self):
        return GeoDataset(
            data_vars=dict(
                mydata=xr.Variable(
                    dims=('band', 'y', 'x'),
                    data=np.arange(2 * 3 * 4).reshape((2, 3, 4)),
                ),
            ),
            coords=dict(
                y=[0, 10000, 20000],
                x=[0, 10000, 20000, 30000],
            ),
        )

    def test_add_crsdef_when_local(self, dset3):
        local = SpatialReference.local(5, 60)
        new_dset = dset3.create_grid_mapping(local)
        new_dset = new_dset.create_geocoords(['x', 'y'])
        assert set(new_dset.crs_def.attrs.keys()) == {
            'false_easting',
            'false_northing',
            'latitude_of_projection_origin',
            'longitude_of_central_meridian',
            'scale_factor_at_central_meridian',
            'crs_wkt',
            'geographic_crs_name',
            'grid_mapping_name',
            'horizontal_datum_name',
            'inverse_flattening',
            'long_name',
            'prime_meridian_name',
            'projected_crs_name',
            'reference_ellipsoid_name',
            'semi_major_axis',
            'spatial_ref',
            'towgs84'
        }
