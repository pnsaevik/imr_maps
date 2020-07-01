from imr.maps import gyte


class Test_gyte:
    def test_returns_nonempty_dataset_when_default_options(self):
        layer_name = 'fisk:hyse_nea_bw'
        ds = gyte.gyte(layer_name)
        assert ds.GetLayerCount() > 0
