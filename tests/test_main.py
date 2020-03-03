from imr.farms import wfs
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


def test_resource_returns_existing_file():
    import os
    fname = wfs.resource('layer_262', 'fiskdir', recompute=False)
    assert os.path.isfile(fname)


class Test_locations:
    @pytest.fixture(scope='class')
    def locations(self):
        with wfs.locations() as dset:
            yield dset

    def test_correct_name_and_location(self, locations):
        a = locations.sel(record=23015)
        assert a.navn.values.item().decode('utf8') == 'FLØDEVIGEN'
        assert a.lat.values.item() == 58.424515
        assert a.lon.values.item() == 8.756882
