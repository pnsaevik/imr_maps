import imr.farms
import pytest


@pytest.fixture(scope='module')
def fiskdir_wfs():
    return imr.farms.get_fiskdir_wfs()


class Test_get_layer:
    def test_returns_layer_name_if_title_match(self, fiskdir_wfs):
        title = 'Akvakultur - lokaliteter'
        layer = imr.farms.get_layer(title, fiskdir_wfs)
        assert layer == 'layer_262'

    def test_returns_none_if_no_match(self, fiskdir_wfs):
        title = 'No title'
        layer = imr.farms.get_layer(title, fiskdir_wfs)
        assert layer is None
