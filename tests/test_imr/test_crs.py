from imr.maps import SpatialReference, set_crs, change_crs
from osgeo import osr
import numpy as np
import pytest
import xarray as xr


class Test_set_crs:
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

    def test_adds_grid_mapping_when_empty_dataset(self):
        dset = xr.Dataset()
        wgs84 = SpatialReference.from_epsg(4326)
        new_dset = set_crs(dset, wgs84)
        assert 'crs_def' in new_dset.data_vars
        assert 'grid_mapping_name' in new_dset.crs_def.attrs

    def test_sets_coordinate_attributes_if_specified(self):
        dset = xr.Dataset(coords=dict(lat=[59, 60, 61], lon=[4, 5, 6, 7]))

        wgs84 = SpatialReference.from_epsg(4326)
        new_dset = set_crs(dset, wgs84, coords=['lon', 'lat'])

        # Attributes are assigned to coordinates in the return value
        assert new_dset.coords['lon'].attrs['standard_name'] == 'longitude'
        assert new_dset.coords['lon'].attrs['axis'] == 'X'
        assert new_dset.coords['lat'].attrs['standard_name'] == 'latitude'
        assert new_dset.coords['lat'].attrs['axis'] == 'Y'

        # No change in the original dataset
        assert 'standard_name' not in dset.coords['lon'].attrs

    def test_adds_gridmapping_to_data_vars_if_specified(self):
        dset = xr.Dataset(
            data_vars=dict(myvar=(('lat', 'lon'), [[1, 2, 3], [4, 5, 6]])))
        wgs84 = SpatialReference.from_epsg(4326)
        new_dset = set_crs(dset, wgs84, data_vars=['myvar'])

        assert new_dset.data_vars['myvar'].attrs['grid_mapping'] == 'crs_def'

    def test_can_use_existing_gridmapping_variable(self):
        wgs84 = SpatialReference.from_epsg(4326)
        dset = xr.Dataset(
            data_vars=dict(myvar=(('lat', 'lon'), [[1, 2, 3], [4, 5, 6]])),
            coords=dict(lat=[59, 60], lon=[4, 5, 6]),
        )

        # First set the crs. Don't do anything to coords or data_vars.
        dset = set_crs(dset, wgs84)
        assert 'standard_name' not in dset.lon.attrs
        assert 'grid_mapping' not in dset.myvar.attrs

        # Now rename the crs, and apply to coords and data_vars.
        dset = dset.rename(crs_def='my_crs_def')
        dset = set_crs(dset, 'my_crs_def', ['lon', 'lat'], ['myvar'])

        assert dset.lon.attrs['standard_name'] == 'longitude'
        assert dset.myvar.attrs['grid_mapping'] == 'my_crs_def'


class Test_change_crs:
    def test_unchanged_when_equal_crs(self):
        wgs84 = SpatialReference.from_epsg(4326)
        dset = set_crs(
            dset=xr.Dataset(
                data_vars=dict(myvar=(('lat', 'lon'), [[1., 2, 3], [4, 5, 6]])),
                coords=dict(lat=[59., 60], lon=[4., 5, 6]),
            ),
            crs=wgs84,
            coords=['lon', 'lat'],
            data_vars=['myvar'],
        )

        dset_new = change_crs(
            dset=dset, old_coords=['lon', 'lat'], old_crs='crs_def',
            new_coords=['lon', 'lat'], new_crs=wgs84,
        )

        assert str(dset_new) == str(dset)

    def test_correct_when_change_from_wgs84_to_utm(self):
        wgs84 = SpatialReference.from_epsg(4326)
        utm = SpatialReference.from_epsg(25831)
        dset = xr.Dataset(
            data_vars=dict(myvar=(('lat', 'lon'), [[1., 2, 3], [4, 5, 6]])),
            coords=dict(lat=[59., 60], lon=[4., 5, 6]),
        )
        dset_wgs84 = set_crs(dset, wgs84, ['lon', 'lat'], ['myvar'])

        dset_utm = change_crs(
            dset=dset_wgs84, old_coords=['lon', 'lat'], old_crs='crs_def',
            new_coords=['x', 'y'], new_crs=utm,
        )

        # Correct values
        x = dset_utm.x.values.astype(int).tolist()
        y = dset_utm.y.values.astype(int).tolist()
        assert x == [[557450, 614893, 672319], [555776, 611544, 667294]]
        assert y == [[6540481, 6541771, 6543920], [6651832, 6653097, 6655205]]

        # Correct attributes
        assert dset_utm.crs_def.grid_mapping_name == 'transverse_mercator'
        assert dset_utm.x.standard_name == 'projection_x_coordinate'
        assert dset_utm.myvar.grid_mapping == 'crs_def'


class Test_from_epsg:
    def test_is_valid_spatial_reference(self):
        sr = SpatialReference.from_epsg(4326)
        assert isinstance(sr, osr.SpatialReference)
        assert sr.ExportToWkt()


class Test_from_wkt:
    def test_is_valid_spatial_reference(self):
        sr = SpatialReference.from_wkt('GEOGCS["WGS 84",DATUM["WGS_1984"]]')
        assert isinstance(sr, osr.SpatialReference)
        assert sr.ExportToWkt()


class Test_local:
    def test_is_valid_spatial_reference(self):
        sr = SpatialReference.local(lon=5, lat=60)
        assert isinstance(sr, osr.SpatialReference)
        assert sr.ExportToWkt()


class Test_nf160:
    def test_is_valid_spatial_reference(self):
        sr = SpatialReference.nf160('A01')
        assert isinstance(sr, osr.SpatialReference)
        assert sr.ExportToWkt()


class Test_nk800:
    def test_is_valid_spatial_reference(self):
        sr = SpatialReference.nk800()
        assert isinstance(sr, osr.SpatialReference)
        assert sr.ExportToWkt()


class Test_transform:
    def test_unchanged_when_wgs84_to_wgs84(self):
        lat = np.array([0, 60])
        lon = np.array([0, 5])
        wgs84 = SpatialReference.from_epsg(4326)
        nlon, nlat = SpatialReference.transform(lon, lat, wgs84, wgs84)

        assert np.linalg.norm(lat - nlat, ord=1) < 1e-8
        assert np.linalg.norm(lat - nlat, ord=1) < 1e-8

    def test_correct_shape_when_empty_input(self):
        lat = np.array([])
        lon = np.array([])
        wgs84 = SpatialReference.from_epsg(4326)
        nlon, nlat = SpatialReference.transform(lon, lat, wgs84, wgs84)

        assert nlat.tolist() == []
        assert nlon.tolist() == []

    def test_correct_shape_when_matrix_input(self):
        lat = np.linspace(5, 6, 12).reshape((4, 3))
        lon = np.linspace(60, 61, 12).reshape((4, 3))
        wgs84 = SpatialReference.from_epsg(4326)
        nlon, nlat = SpatialReference.transform(lon, lat, wgs84, wgs84)

        assert nlat.shape == lat.shape
        assert nlon.shape == lon.shape

    def test_unchanged_when_wgs84_to_etrs89(self):
        lat = np.array([0, 60])
        lon = np.array([0, 5])
        wgs84 = SpatialReference.from_epsg(4326)
        etrs89 = SpatialReference.from_epsg(4258)
        nlon, nlat = SpatialReference.transform(lon, lat, wgs84, etrs89)

        assert np.linalg.norm(lat - nlat, ord=1) < 1e-8
        assert np.linalg.norm(lat - nlat, ord=1) < 1e-8

    def test_zero_when_wgs84_to_local_center(self):
        lon = 5
        lat = 60
        wgs84 = SpatialReference.from_epsg(4326)
        local = SpatialReference.local(lon, lat)
        new_points = SpatialReference.transform([lon], [lat], wgs84, local)
        assert np.linalg.norm(new_points, ord=1) < 1e-8

    def test_nautical_mile_when_wgs84_to_local_center_plus_lat_minute(self):
        lon = 5
        lat = 60
        wgs84 = SpatialReference.from_epsg(4326)
        local = SpatialReference.local(lon, lat)
        nlon, nlat = SpatialReference.transform([lon], [lat + 1/60], wgs84, local)
        assert np.abs(nlon) < 1e-8
        assert np.abs(nlat - 1857) < 1.0

    def test_half_nautical_mile_when_wgs84_to_local_center_plus_lon_minute(self):
        lon = 5
        lat = 60
        wgs84 = SpatialReference.from_epsg(4326)
        local = SpatialReference.local(lon, lat)
        nlon, nlat = SpatialReference.transform([lon + 1/60], [lat], wgs84, local)
        assert np.abs(nlon - 930) < 1
        assert np.abs(nlat) < 1

    def test_nk800_to_wgs84(self):
        xi = [0, 1000, 1000, 0]
        eta = [0, 0, 500, 500]
        wgs84 = SpatialReference.from_epsg(4326)
        nk800 = SpatialReference.nk800()
        lon, lat = SpatialReference.transform(xi, eta, nk800, wgs84)
        assert np.all(np.isclose(
            lat, [55.90836993, 61.91497602, 63.91826663, 57.47693917]))
        assert np.all(np.isclose(
            lon, [9.19459011, 16.70710853, 10.04516874, 3.43554155]))

    def test_wgs84_to_nk800(self):
        lat = [55.90836993, 61.91497602, 63.91826663, 57.47693917]
        lon = [9.19459011, 16.70710853, 10.04516874, 3.43554155]
        wgs84 = SpatialReference.from_epsg(4326)
        nk800 = SpatialReference.nk800()
        xi, eta = SpatialReference.transform(lon, lat, wgs84, nk800)
        assert np.all(np.isclose(xi, [0, 1000, 1000, 0], atol=1e-5))
        assert np.all(np.isclose(eta, [0, 0, 500, 500], atol=1e-5))

    def test_nf160_a01_to_wgs84(self):
        xi = [0, 1000, 1000, 0]
        eta = [0, 0, 500, 500]
        nf160_A01 = SpatialReference.nf160('A01')
        wgs84 = SpatialReference.from_epsg(4326)
        lon, lat = SpatialReference.transform(xi, eta, nf160_A01, wgs84)
        assert np.all(np.isclose(
            lat, [57.72536405, 58.95227724, 59.31714908, 58.07345413]))
        assert np.all(np.isclose(
            lon, [9.89245542, 11.27116288, 10.0741957,  8.72794269]))

    def test_nf160_wgs84_to_nf160_a01(self):
        lat = [57.72536405, 58.95227724, 59.31714908, 58.07345413]
        lon = [9.89245542, 11.27116288, 10.0741957,  8.72794269]
        nf160_A01 = SpatialReference.nf160('A01')
        wgs84 = SpatialReference.from_epsg(4326)
        xi, eta = SpatialReference.transform(lon, lat, wgs84, nf160_A01)
        assert np.all(np.isclose(xi, [0, 1000, 1000, 0], atol=1e-5))
        assert np.all(np.isclose(eta, [0, 0, 500, 500], atol=1e-5))

    def test_nk800_to_nk800m(self):
        x = [0, 1, 2]
        y = [0, 0, 1]
        nk800m = SpatialReference.nk800(metric_unit=True)
        nk800 = SpatialReference.nk800()
        xm, ym = SpatialReference.transform(x, y, nk800, nk800m)
        assert np.all(np.isclose(xm, [0, 800, 1600], atol=1e-5))
        assert np.all(np.isclose(ym, [0, 0, 800], atol=1e-5))

    def test_nf160m_to_nf160(self):
        x = [0, 160, 320]
        y = [0, 0, 160]
        nf160_A01m = SpatialReference.nf160('A01', metric_unit=True)
        nf160_A01 = SpatialReference.nf160('A01')
        xm, ym = SpatialReference.transform(x, y, nf160_A01m, nf160_A01)
        assert np.all(np.isclose(xm, [0, 1, 2], atol=1e-5))
        assert np.all(np.isclose(ym, [0, 0, 1], atol=1e-5))
