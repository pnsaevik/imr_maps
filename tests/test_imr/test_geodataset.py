from imr.maps import crs, geodataset
import xarray as xr
import pytest
import numpy as np


class Test_add_crs_to_dataset:
    @pytest.fixture(scope='class')
    def dset(self):
        return xr.Dataset(
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

    def test_add_crsdef_when_wgs84(self, dset):
        wgs84 = crs.projection_from_epsg(4326)
        new_dset = geodataset.add_crs_to_dataset(dset, ['lon', 'lat'], wgs84)
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

    def test_add_coordattr_when_wgs84(self, dset):
        wgs84 = crs.projection_from_epsg(4326)
        new_dset = geodataset.add_crs_to_dataset(dset, ['lon', 'lat'], wgs84)
        assert set(new_dset.lat.attrs.keys()) == {
            'standard_name', 'units', 'axis'}
        assert set(new_dset.lon.attrs.keys()) == {
            'standard_name', 'units', 'axis'}

    def test_add_gridmappings_when_wgs84(self, dset):
        wgs84 = crs.projection_from_epsg(4326)
        new_dset = geodataset.add_crs_to_dataset(dset, ['lon', 'lat'], wgs84)
        assert set(new_dset.mydata.attrs.keys()) == {'grid_mapping'}

    def test_add_globals_when_wgs84(self, dset):
        wgs84 = crs.projection_from_epsg(4326)
        new_dset = geodataset.add_crs_to_dataset(dset, ['lon', 'lat'], wgs84)
        assert set(new_dset.attrs.keys()) == {'Conventions'}

    @pytest.fixture(scope='class')
    def dset2(self):
        return xr.Dataset(
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
        utm33n = crs.projection_from_epsg(32633)
        new_dset = geodataset.add_crs_to_dataset(dset2, ['x', 'y'], utm33n)
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
        utm33n = crs.projection_from_epsg(32633)
        new_dset = geodataset.add_crs_to_dataset(dset2, ['x', 'y'], utm33n)
        assert set(new_dset.x.attrs.keys()) == {
            'standard_name', 'axis'}
        assert set(new_dset.y.attrs.keys()) == {
            'standard_name', 'axis'}

    @pytest.fixture(scope='class')
    def dset3(self):
        return xr.Dataset(
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
        local = crs.projection_local(5, 60)
        new_dset = geodataset.add_crs_to_dataset(dset3, ['x', 'y'], local)
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
