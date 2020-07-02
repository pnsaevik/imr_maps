from imr.maps import coast
import pytest
import os


is_travis = "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true"


class Test_coastlines:
    @pytest.mark.skipif(is_travis, reason='No access to ssh resource')
    def test_returns_nonempty_xarray(self):
        latlim = [60, 60.01]
        lonlim = [5, 5.01]
        c = coast.coastlines(latlim, lonlim)
        assert c.dims['patch_num'] > 0
        assert c.dims['node_num'] > 0
        assert len(c.latitude)
        assert len(c.longitude)
        assert len(c.patchsize)

    @pytest.mark.skipif(is_travis, reason='No access to ssh resource')
    def test_merges_patches(self):
        latlim = [59.961123, 59.965186]
        lonlim = [5.048765, 5.052984]
        c = coast.coastlines(latlim, lonlim)
        assert c.dims['patch_num'] == 1

    @pytest.mark.skipif(is_travis, reason='No access to ssh resource')
    def test_returns_valid_result_when_no_patches(self):
        latlim = [59.0, 59.01]
        lonlim = [5.0, 5.01]
        c = coast.coastlines(latlim, lonlim)
        assert c.dims['patch_num'] == 0
        assert c.dims['node_num'] == 0
        assert c.latitude.values.tolist() == []
        assert c.longitude.values.tolist() == []

    @pytest.mark.skipif(is_travis, reason='No access to ssh resource')
    def test_returns_nonempty_xarray_when_gshhs(self):
        latlim = [60, 60.01]
        lonlim = [5, 5.01]
        c = coast.coastlines(latlim, lonlim, source='gshhs')
        assert c.dims['patch_num'] > 0
        assert c.dims['node_num'] > 0
        assert len(c.latitude)
        assert len(c.longitude)
        assert len(c.patchsize)
