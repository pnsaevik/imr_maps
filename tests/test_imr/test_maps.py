from imr.maps import crs
import xarray as xr
import pytest
import numpy as np


class Test_projection_from_dataset:
    def test_raises_valueerror_if_no_spatial_ref(self):
        with pytest.raises(ValueError):
            empty_dset = xr.Dataset()
            crs.projection_from_dataset(empty_dset)

    def test_returns_proj_if_spatial_ref_present(self):
        wkt = crs.projection_from_epsg(4326).ExportToWkt()

        dset = xr.Dataset(
            data_vars=dict(
                my_transform=xr.Variable(
                    dims=(),
                    data=0,
                    attrs=dict(
                        spatial_ref=wkt,
                    ),
                )
            )
        )

        proj = crs.projection_from_dataset(dset)
        assert wkt == proj.ExportToWkt()


class Test_projection_local:
    def test_returns_projection(self):
        proj = crs.projection_local(lon=5, lat=60)
        assert proj.ExportToWkt().startswith('PROJCS')


class Test_transform:
    def test_unchanged_when_wgs84_to_wgs84(self):
        lat = np.array([0, 60])
        lon = np.array([0, 5])
        wgs84 = crs.projection_from_epsg(4326)
        nlon, nlat = crs.transform(lon, lat, wgs84, wgs84)

        assert np.linalg.norm(lat - nlat, ord=1) < 1e-8
        assert np.linalg.norm(lat - nlat, ord=1) < 1e-8

    def test_correct_shape_when_empty_input(self):
        lat = np.array([])
        lon = np.array([])
        wgs84 = crs.projection_from_epsg(4326)
        nlon, nlat = crs.transform(lon, lat, wgs84, wgs84)

        assert nlat.tolist() == []
        assert nlon.tolist() == []

    def test_unchanged_when_wgs84_to_etrs89(self):
        lat = np.array([0, 60])
        lon = np.array([0, 5])
        wgs84 = crs.projection_from_epsg(4326)
        etrs89 = crs.projection_from_epsg(4258)
        nlon, nlat = crs.transform(lon, lat, wgs84, etrs89)

        assert np.linalg.norm(lat - nlat, ord=1) < 1e-8
        assert np.linalg.norm(lat - nlat, ord=1) < 1e-8

    def test_zero_when_wgs84_to_local_center(self):
        lon = 5
        lat = 60
        wgs84 = crs.projection_from_epsg(4326)
        local = crs.projection_local(lon, lat)
        new_points = crs.transform([lon], [lat], wgs84, local)
        assert np.linalg.norm(new_points, ord=1) < 1e-8

    def test_nautical_mile_when_wgs84_to_local_center_plus_lat_minute(self):
        lon = 5
        lat = 60
        wgs84 = crs.projection_from_epsg(4326)
        local = crs.projection_local(lon, lat)
        nlon, nlat = crs.transform([lon], [lat + 1/60], wgs84, local)
        assert np.abs(nlon) < 1e-8
        assert np.abs(nlat - 1857) < 1.0

    def test_half_nautical_mile_when_wgs84_to_local_center_plus_lon_minute(self):
        lon = 5
        lat = 60
        wgs84 = crs.projection_from_epsg(4326)
        local = crs.projection_local(lon, lat)
        nlon, nlat = crs.transform([lon + 1/60], [lat], wgs84, local)
        assert np.abs(nlon - 930) < 1
        assert np.abs(nlat) < 1

    def test_nk800_to_wgs84(self):
        xi = [0, 1000, 1000, 0]
        eta = [0, 0, 500, 500]
        wgs84 = crs.projection_from_epsg(4326)
        nk800 = crs.projection_nk800()
        lon, lat = crs.transform(xi, eta, nk800, wgs84)
        assert np.all(np.isclose(
            lat, [55.90836993, 61.91497602, 63.91826663, 57.47693917]))
        assert np.all(np.isclose(
            lon, [9.19459011, 16.70710853, 10.04516874, 3.43554155]))

    def test_wgs84_to_nk800(self):
        lat = [55.90836993, 61.91497602, 63.91826663, 57.47693917]
        lon = [9.19459011, 16.70710853, 10.04516874, 3.43554155]
        wgs84 = crs.projection_from_epsg(4326)
        nk800 = crs.projection_nk800()
        xi, eta = crs.transform(lon, lat, wgs84, nk800)
        assert np.all(np.isclose(xi, [0, 1000, 1000, 0], atol=1e-5))
        assert np.all(np.isclose(eta, [0, 0, 500, 500], atol=1e-5))

    def test_nf160_a01_to_wgs84(self):
        xi = [0, 1000, 1000, 0]
        eta = [0, 0, 500, 500]
        nf160_A01 = crs.projection_nf160('A01')
        wgs84 = crs.projection_from_epsg(4326)
        lon, lat = crs.transform(xi, eta, nf160_A01, wgs84)
        assert np.all(np.isclose(
            lat, [57.72536405, 58.95227724, 59.31714908, 58.07345413]))
        assert np.all(np.isclose(
            lon, [9.89245542, 11.27116288, 10.0741957,  8.72794269]))

    def test_nf160_wgs84_to_nf160_a01(self):
        lat = [57.72536405, 58.95227724, 59.31714908, 58.07345413]
        lon = [9.89245542, 11.27116288, 10.0741957,  8.72794269]
        nf160_A01 = crs.projection_nf160('A01')
        wgs84 = crs.projection_from_epsg(4326)
        xi, eta = crs.transform(lon, lat, wgs84, nf160_A01)
        assert np.all(np.isclose(xi, [0, 1000, 1000, 0], atol=1e-5))
        assert np.all(np.isclose(eta, [0, 0, 500, 500], atol=1e-5))

    def test_nk800_to_nk800m(self):
        x = [0, 1, 2]
        y = [0, 0, 1]
        nk800m = crs.projection_nk800(metric_unit=True)
        nk800 = crs.projection_nk800()
        xm, ym = crs.transform(x, y, nk800, nk800m)
        assert np.all(np.isclose(xm, [0, 800, 1600], atol=1e-5))
        assert np.all(np.isclose(ym, [0, 0, 800], atol=1e-5))

    def test_nf160m_to_nf160(self):
        x = [0, 160, 320]
        y = [0, 0, 160]
        nf160_A01m = crs.projection_nf160('A01', metric_unit=True)
        nf160_A01 = crs.projection_nf160('A01')
        xm, ym = crs.transform(x, y, nf160_A01m, nf160_A01)
        assert np.all(np.isclose(xm, [0, 1, 2], atol=1e-5))
        assert np.all(np.isclose(ym, [0, 0, 1], atol=1e-5))
