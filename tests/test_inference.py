import pytest
from inference import get_action, run_episode

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

def test_run_episode_reset_fallback(mocker):
    # Mock requests.post to always raise an exception
    mocker.patch("inference.requests.post", side_effect=Exception("Connection Error"))

    # Mock step_environment to immediately finish the episode
    mock_step = mocker.patch("inference.step_environment", return_value=({}, 0.0, True, None))

    # Mock get_action to avoid hitting the actual API
    mocker.patch("inference.get_action", return_value="monitor")

    # Mock print to keep output clean
    mocker.patch("builtins.print")

    # Run the episode
    run_episode("test_task")

    # Expected fallback observation that reset_environment should return when requests.post fails
    expected_fallback_obs = {
        "cpu_usage_percent": 0.0,
        "packet_rate_pps": 0.0,
        "active_connections": 0,
        "bandwidth_mbps": 0.0,
        "memory_usage_percent": 30.0,
        "system_health": 100.0,
    }

    # Verify that step_environment was called with the fallback observation
    # The first argument is action ("monitor"), the second is current_obs
    mock_step.assert_called_once()
    args, _ = mock_step.call_args

    # args[1] should be the fallback obs passed from reset_environment
    assert args[1] == expected_fallback_obs
