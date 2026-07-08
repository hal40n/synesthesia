import json
from unittest.mock import patch

import pytest

from syn.config import Config
from syn.llm.client import LLMClient
from syn.llm.schema import LLMInput, LLMOutput

VALID_JSON = json.dumps(
    {"base_hue": 120, "hue_offset": 10, "saturation": 0.5, "brightness": 0.6}
)


@pytest.fixture
def llm_input() -> LLMInput:
    return LLMInput(
        key="C major",
        pitch_classes=["C", "E", "G"],
        frequencies=[261.6, 329.6, 392.0],
        dynamics="medium",
        density="normal",
    )


class TestConfigIntegration:
    def test_client_reads_settings_from_config(self, monkeypatch):
        """Client must use Config as the single source of settings,
        not read environment variables on its own."""
        monkeypatch.setattr(Config, "SYN_LLM_PROVIDER", "ollama")
        monkeypatch.setattr(Config, "SYN_LLM_MODEL", "cfg-model")
        monkeypatch.setattr(Config, "SYN_LLM_BASE_URL", "http://cfg-host:1111")

        client = LLMClient(prompt="p")

        assert client.provider == "ollama"
        assert client.model == "cfg-model"
        assert client.base_url == "http://cfg-host:1111"


class TestParseOutput:
    def test_plain_json(self):
        client = LLMClient(prompt="p")
        output = client._parse_output(VALID_JSON)
        assert output == LLMOutput(base_hue=120.0, hue_offset=10.0, saturation=0.5, brightness=0.6)

    def test_json_fenced_with_language(self):
        client = LLMClient(prompt="p")
        output = client._parse_output(f"```json\n{VALID_JSON}\n```")
        assert output.base_hue == 120.0

    def test_json_fenced_plain(self):
        client = LLMClient(prompt="p")
        output = client._parse_output(f"```\n{VALID_JSON}\n```")
        assert output.base_hue == 120.0

    def test_invalid_json_raises(self):
        client = LLMClient(prompt="p")
        with pytest.raises(ValueError, match="Failed to parse"):
            client._parse_output("not json at all")

    def test_out_of_range_values_raise(self):
        client = LLMClient(prompt="p")
        bad = json.dumps({"base_hue": 999, "hue_offset": 0, "saturation": 0.5, "brightness": 0.5})
        with pytest.raises(ValueError):
            client._parse_output(bad)


class TestInterpretRetry:
    def test_retries_once_on_failure(self, llm_input, valid_output):
        client = LLMClient(prompt="p")
        client.provider = "lmstudio"
        with patch.object(
            client,
            "_lmstudio_interpret",
            side_effect=[RuntimeError("transient"), valid_output],
        ) as mock_call:
            result = client.interpret(llm_input)
        assert result == valid_output
        assert mock_call.call_count == 2

    def test_raises_after_all_attempts_fail(self, llm_input):
        client = LLMClient(prompt="p")
        client.provider = "lmstudio"
        with patch.object(
            client,
            "_lmstudio_interpret",
            side_effect=RuntimeError("down"),
        ) as mock_call:
            with pytest.raises(RuntimeError, match="down"):
                client.interpret(llm_input)
        assert mock_call.call_count == 2

    def test_unsupported_provider_fails_without_retry(self, llm_input):
        client = LLMClient(prompt="p")
        client.provider = "unknown-provider"
        with pytest.raises(RuntimeError, match="Unsupported LLM provider"):
            client.interpret(llm_input)


class TestHttpCalls:
    def _mock_response(self, payload):
        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return payload

        return FakeResponse()

    def test_lmstudio_request_shape(self, llm_input):
        client = LLMClient(prompt="system prompt", temperature=0.3)
        client.base_url = "http://test:1234"
        client.model = "m"
        payload = {"choices": [{"message": {"content": VALID_JSON}}]}
        with patch("syn.llm.client.requests.post", return_value=self._mock_response(payload)) as post:
            output = client._lmstudio_interpret(llm_input)

        assert output.base_hue == 120.0
        url = post.call_args.args[0] if post.call_args.args else post.call_args.kwargs["url"]
        assert url == "http://test:1234/v1/chat/completions"
        body = post.call_args.kwargs["json"]
        assert body["temperature"] == 0.3
        assert body["messages"][0] == {"role": "system", "content": "system prompt"}

    def test_ollama_request_shape(self, llm_input):
        client = LLMClient(prompt="system prompt", temperature=0.7)
        client.base_url = "http://test:11434"
        client.model = "m"
        payload = {"message": {"content": VALID_JSON}}
        with patch("syn.llm.client.requests.post", return_value=self._mock_response(payload)) as post:
            output = client._ollama_interpret(llm_input)

        assert output.base_hue == 120.0
        url = post.call_args.args[0] if post.call_args.args else post.call_args.kwargs["url"]
        assert url == "http://test:11434/api/chat"
        body = post.call_args.kwargs["json"]
        assert body["options"]["temperature"] == 0.7
