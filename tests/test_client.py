import json
from unittest.mock import patch

import pytest
import requests
from conftest import VALID_OUTPUT

from syn.config import Config
from syn.llm.client import LLMClient
from syn.llm.schema import LLMInput, output_to_json

VALID_JSON = output_to_json(VALID_OUTPUT)


def make_client(**overrides) -> LLMClient:
    kwargs = dict(
        prompt="p",
        temperature=0.0,
        provider="lmstudio",
        base_url="http://test:1234",
        model="m",
    )
    kwargs.update(overrides)
    return LLMClient(**kwargs)


@pytest.fixture
def llm_input() -> LLMInput:
    return LLMInput(
        key="C major",
        pitch_classes=["C", "E", "G"],
        frequencies=[261.6, 329.6, 392.0],
        dynamics="medium",
        density="normal",
    )


class TestConstruction:
    def test_settings_are_injected_not_read_from_env(self):
        """Settings come in explicitly; the client must not depend on
        Config/env so it stays importable and usable standalone."""
        client = make_client(provider="ollama", base_url="http://h:1", model="mm")
        assert client.provider == "ollama"
        assert client.base_url == "http://h:1"
        assert client.model == "mm"

    def test_unsupported_provider_fails_at_construction(self):
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            make_client(provider="unknown-provider")


class TestParseOutput:
    def test_plain_json(self):
        assert make_client()._parse_output(VALID_JSON) == VALID_OUTPUT

    def test_json_fenced_with_language(self):
        assert make_client()._parse_output(f"```json\n{VALID_JSON}\n```") == VALID_OUTPUT

    def test_json_fenced_plain(self):
        assert make_client()._parse_output(f"```\n{VALID_JSON}\n```") == VALID_OUTPUT

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Failed to parse"):
            make_client()._parse_output("not json at all")

    def test_out_of_range_values_raise(self):
        bad = json.dumps({"base_hue": 999, "hue_offset": 0, "saturation": 0.5, "brightness": 0.5})
        with pytest.raises(ValueError):
            make_client()._parse_output(bad)


class TestInterpretRetry:
    def test_transient_error_is_retried_once(self, llm_input):
        client = make_client()
        with patch.object(
            client,
            "_lmstudio_interpret",
            side_effect=[requests.ConnectionError("reset"), VALID_OUTPUT],
        ) as mock_call:
            assert client.interpret(llm_input) == VALID_OUTPUT
        assert mock_call.call_count == 2

    def test_malformed_output_is_retried(self, llm_input):
        client = make_client()
        with patch.object(
            client,
            "_lmstudio_interpret",
            side_effect=[ValueError("Failed to parse LLM output"), VALID_OUTPUT],
        ) as mock_call:
            assert client.interpret(llm_input) == VALID_OUTPUT
        assert mock_call.call_count == 2

    def test_raises_with_first_error_chained(self, llm_input):
        client = make_client()
        first = requests.ConnectionError("first")
        second = requests.Timeout("second")
        with patch.object(
            client, "_lmstudio_interpret", side_effect=[first, second]
        ) as mock_call:
            with pytest.raises(requests.Timeout, match="second") as exc_info:
                client.interpret(llm_input)
        assert mock_call.call_count == 2
        assert exc_info.value.__cause__ is first

    def test_deterministic_error_is_not_retried(self, llm_input):
        client = make_client()
        with patch.object(
            client,
            "_lmstudio_interpret",
            side_effect=requests.HTTPError("404 model not found"),
        ) as mock_call:
            with pytest.raises(requests.HTTPError):
                client.interpret(llm_input)
        assert mock_call.call_count == 1


class TestHttpCalls:
    def _mock_response(self, payload):
        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return payload

        return FakeResponse()

    def test_lmstudio_request_shape(self, llm_input):
        client = make_client(prompt="system prompt", temperature=0.3)
        payload = {"choices": [{"message": {"content": VALID_JSON}}]}
        with patch("syn.llm.client.requests.post", return_value=self._mock_response(payload)) as post:
            output = client._lmstudio_interpret(llm_input)

        assert output == VALID_OUTPUT
        url = post.call_args.args[0] if post.call_args.args else post.call_args.kwargs["url"]
        assert url == "http://test:1234/v1/chat/completions"
        body = post.call_args.kwargs["json"]
        assert body["temperature"] == 0.3
        assert body["messages"][0] == {"role": "system", "content": "system prompt"}

    def test_ollama_request_shape(self, llm_input):
        client = make_client(
            prompt="system prompt", temperature=0.7, provider="ollama", base_url="http://test:11434"
        )
        payload = {"message": {"content": VALID_JSON}}
        with patch("syn.llm.client.requests.post", return_value=self._mock_response(payload)) as post:
            output = client._ollama_interpret(llm_input)

        assert output == VALID_OUTPUT
        url = post.call_args.args[0] if post.call_args.args else post.call_args.kwargs["url"]
        assert url == "http://test:11434/api/chat"
        body = post.call_args.kwargs["json"]
        assert body["options"]["temperature"] == 0.7
