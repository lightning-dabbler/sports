import pytest

import sports.shared.container


def extractor(self):
    self.data_extracts = self.raw_data["foo"][0]["data"]


class TestBaseContainer:
    @pytest.mark.parametrize("raw_data,extractor,expected", [({"foo": [{"data": {}}]}, extractor, {})])
    def test_extraction(self, raw_data, extractor, expected):
        container = sports.shared.container.BaseContainer(raw_data=raw_data)
        container.extraction(extractor)
        assert container.data_extracts == expected, "Successful Extraction"
