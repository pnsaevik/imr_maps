import pytest
from imr.maps import farms


class Test_locations:
    @pytest.fixture(scope='class')
    def locations(self):
        with farms.locations() as dset:
            yield dset

    def test_correct_name_and_location(self, locations):
        a = locations.sel(record=23015)
        assert a.navn.values.item().decode('utf8') == 'FLØDEVIGEN'
        assert a.lat.values.item() == 58.424515
        assert a.lon.values.item() == 8.756882


class Test_areas:
    @pytest.fixture(scope='class')
    def areas(self):
        with farms.areas() as dset:
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
