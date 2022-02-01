import pytest

import sports.operations.container


class TestBaseContainer:
    @pytest.mark.parametrize(
        "raw_data,extractor,expected", [({"foo": [{"data": {}}]}, lambda x: x["foo"][0]["data"], {})]
    )
    def test_extraction(self, raw_data, extractor, expected):
        container = sports.operations.container.BaseContainer(raw_data=raw_data)
        container.extraction(extractor)
        assert container.data_extracts == expected, "Successful Extraction"
