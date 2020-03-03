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


class Test_areas:
    @pytest.fixture(scope='class')
    def areas(self):
        with wfs.areas() as dset:
            yield dset

    def test_correct_name_and_location(self, areas):
        a = areas.sel(record=11488)
        assert a.navn.values.item().decode('utf8') == 'BRATTAVIKA'
        assert a.ogc_wkt.values.item().decode('utf8') == (
            'POLYGON ((-38902.007508 6695649.481201,'
            '-38956.470111 6696165.972515,-38926.039136 6696244.396389,'
            '-38897.917527 6696249.609714,-38744.108817 6696181.643866,'
            '-38690.019275 6695668.944893,-38902.007508 6695649.481201))')
        assert a.transverse_mercator.spatial_ref.startswith(
            'PROJCS["WGS 84 / UTM zone 33N"')
