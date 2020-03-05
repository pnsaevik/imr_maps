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
