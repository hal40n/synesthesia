import json

import pytest

from syn.llm.schema import LLMInput, LLMOutput, output_to_json, validate_output


class TestValidateOutput:
    def test_valid_output_passes(self, valid_output):
        validate_output(valid_output)  # must not raise

    def test_boundary_values_pass(self):
        validate_output(LLMOutput(base_hue=0, hue_offset=-180, saturation=0.0, brightness=0.0))
        validate_output(LLMOutput(base_hue=360, hue_offset=180, saturation=1.0, brightness=1.0))

    @pytest.mark.parametrize(
        "field,value",
        [
            ("base_hue", -1),
            ("base_hue", 361),
            ("hue_offset", -181),
            ("hue_offset", 181),
            ("saturation", -0.1),
            ("saturation", 1.1),
            ("brightness", -0.1),
            ("brightness", 1.1),
        ],
    )
    def test_out_of_range_raises(self, valid_output, field, value):
        data = {**valid_output.__dict__, field: value}
        with pytest.raises(ValueError):
            validate_output(LLMOutput(**data))


class TestOutputToJson:
    def test_returns_json_roundtrip(self, valid_output):
        result = output_to_json(valid_output)
        assert json.loads(result) == {
            "base_hue": 120.0,
            "hue_offset": 10.0,
            "saturation": 0.5,
            "brightness": 0.6,
        }


class TestLLMInput:
    def test_is_frozen(self):
        llm_input = LLMInput(
            key="C major",
            pitch_classes=["C", "E", "G"],
            frequencies=[261.6, 329.6, 392.0],
            dynamics="medium",
            density="normal",
        )
        with pytest.raises(Exception):
            llm_input.key = "D major"
