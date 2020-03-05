from imr.maps import crs
import xarray as xr
import pytest


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
