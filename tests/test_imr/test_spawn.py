from imr.maps import spawn


class Test_gyte:
    def test_returns_nonempty_dataset_when_default_options(self):
        layer_name = 'utbredelseskart:Hyse_Nordostarktisk'
        ds = spawn.area(layer_name)
        assert ds.GetLayerCount() > 0
