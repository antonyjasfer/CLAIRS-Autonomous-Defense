import pytest
from inference import get_action

def test_get_action_fallback_on_exception(mocker):
    # Mock the OpenAI client call to raise an exception
    mocker.patch("inference.client.chat.completions.create", side_effect=Exception("API Error"))

    # Call the function with a sample history
    history = [
        {"cpu": 10.0, "pps": 100.0, "bw": 1.0, "health": 100.0},
        {"cpu": 10.0, "pps": 100.0, "bw": 1.0, "health": 100.0}
    ]

    # Verify it falls back to "monitor"
    result = get_action(history)
    assert result == "monitor"
