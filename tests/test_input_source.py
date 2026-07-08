import pytest

from syn.input.base import InputSource
from syn.input.factory import create_input_source
from syn.input.static import StaticInputSource
from syn.llm.schema import LLMInput


class TestStaticInputSource:
    def test_read_returns_valid_llm_input(self):
        source = StaticInputSource()
        llm_input = source.read()
        assert isinstance(llm_input, LLMInput)
        assert llm_input.key == "C major"
        assert llm_input.pitch_classes == ["C", "E", "G"]
        assert llm_input.dynamics == "medium"
        assert llm_input.density == "normal"

    def test_key_override(self):
        source = StaticInputSource(key="E minor")
        assert source.read().key == "E minor"

    def test_read_is_deterministic(self):
        source = StaticInputSource()
        assert source.read() == source.read()

    def test_is_an_input_source(self):
        assert isinstance(StaticInputSource(), InputSource)


class TestFactory:
    def test_creates_static_source(self):
        source = create_input_source("static", key="D major")
        assert isinstance(source, StaticInputSource)
        assert source.read().key == "D major"

    def test_unknown_source_fails_explicitly(self):
        with pytest.raises(ValueError, match="Unknown input source"):
            create_input_source("telepathy")
