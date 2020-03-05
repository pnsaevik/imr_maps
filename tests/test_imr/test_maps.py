from imr.maps import crs
import xarray as xr
import pytest


class Test_projection_from_dataset:
    def test_raises_valueerror_if_no_spatial_ref(self):
        with pytest.raises(ValueError):
            empty_dset = xr.Dataset()
            crs.projection_from_dataset(empty_dset)
