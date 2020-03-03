from imr.farms import fiskdir
import pytest


@pytest.fixture(scope='module')
def fiskdir_wfs():
    return fiskdir.get_wfs(fiskdir.URL)


class Test_get_layer:
    def test_returns_layer_name_if_title_match(self, fiskdir_wfs):
        title = 'Akvakultur - lokaliteter'
        layer = fiskdir.get_layer(title, fiskdir_wfs)
        assert layer == 'layer_262'

    def test_returns_none_if_no_match(self, fiskdir_wfs):
        title = 'No title'
        layer = fiskdir.get_layer(title, fiskdir_wfs)
        assert layer is None


def test_writable_location_returns_string():
    assert isinstance(fiskdir.writable_location(), str)
