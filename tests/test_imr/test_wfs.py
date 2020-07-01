from imr.maps import wfs
import pytest


@pytest.fixture(scope='module')
def fiskdir_wfs():
    return wfs.get_wfs(wfs.servers['fiskdir'])


class Test_get_layer:
    def test_returns_layer_name_if_title_match(self, fiskdir_wfs):
        title = 'Akvakultur - lokaliteter'
        layer = wfs.get_layer(title, fiskdir_wfs)
        assert layer == 'layer_262'

    def test_returns_none_if_no_match(self, fiskdir_wfs):
        title = 'No title'
        layer = wfs.get_layer(title, fiskdir_wfs)
        assert layer is None


def test_writable_location_returns_string():
    assert isinstance(wfs.writable_location(), str)


class Test_resource:
    @pytest.fixture(scope='class')
    def sei_bw(self):
        return wfs.resource('fisk:Sei_bw', 'imr_fisk')

    def test_recomputes_if_specified(self, sei_bw):
        import os
        from unittest import mock
        assert os.path.isfile(sei_bw)

        with mock.patch('imr.maps.wfs.download_wfs_layer') as m:
            fname = wfs.resource('fisk:Sei_bw', 'imr_fisk', recompute=True)
            assert fname == sei_bw
            assert m.call_count == 1

    def test_does_not_recompute_if_resource_exists(self, sei_bw):
        import os
        from unittest import mock
        assert os.path.isfile(sei_bw)

        with mock.patch('imr.maps.wfs.download_wfs_layer') as m:
            fname = wfs.resource('fisk:Sei_bw', 'imr_fisk')
            assert fname == sei_bw
            assert m.call_count == 0

    def test_does_not_recompute_if_long_expiration(self, sei_bw):
        import os
        from unittest import mock
        import time
        assert os.path.isfile(sei_bw)
        expires = time.time() - os.path.getmtime(sei_bw) + 1000

        with mock.patch('imr.maps.wfs.download_wfs_layer') as m:
            fname = wfs.resource('fisk:Sei_bw', 'imr_fisk', expires=expires)
            assert fname == sei_bw
            assert m.call_count == 0

    def test_recomputes_if_short_expiration(self, sei_bw):
        import os
        from unittest import mock
        import time
        assert os.path.isfile(sei_bw)
        expires = time.time() - os.path.getmtime(sei_bw) - 1

        with mock.patch('imr.maps.wfs.download_wfs_layer') as m:
            fname = wfs.resource('fisk:Sei_bw', 'imr_fisk', expires=expires)
            assert fname == sei_bw
            assert m.call_count == 1

    def test_returned_file_is_georeferenced_netcdf(self, sei_bw):
        import netCDF4 as nc
        with nc.Dataset(sei_bw) as dset:
            assert 'crs' in dset.variables.keys()
