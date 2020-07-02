from imr.maps import coast


class Test_coastlines:
    def test_returns_nonempty_xarray(self):
        latlim = [60, 60.01]
        lonlim = [5, 5.01]
        c = coast.coastlines(latlim, lonlim)
        assert c.dims['patch_num'] > 0
        assert c.dims['node_num'] > 0
        assert len(c.latitude)
        assert len(c.longitude)
        assert len(c.patchsize)

    def test_merges_patches(self):
        latlim = [59.961123, 59.965186]
        lonlim = [5.048765, 5.052984]
        c = coast.coastlines(latlim, lonlim)
        assert c.dims['patch_num'] == 1

    def test_returns_valid_result_when_no_patches(self):
        latlim = [59.0, 59.01]
        lonlim = [5.0, 5.01]
        c = coast.coastlines(latlim, lonlim)
        assert c.dims['patch_num'] == 0
        assert c.dims['node_num'] == 0
        assert c.latitude.values.tolist() == []
        assert c.longitude.values.tolist() == []

    def test_returns_nonempty_xarray_when_gshhs(self):
        latlim = [60, 60.01]
        lonlim = [5, 5.01]
        c = coast.coastlines(latlim, lonlim, source='gshhs')
        assert c.dims['patch_num'] > 0
        assert c.dims['node_num'] > 0
        assert len(c.latitude)
        assert len(c.longitude)
        assert len(c.patchsize)
