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

def test_run_episode_step_exception(mocker):
    # Setup dummy observation and mock dependencies
    dummy_obs = {
        "cpu_usage_percent": 10.0,
        "packet_rate_pps": 100.0,
        "bandwidth_mbps": 1.0,
        "system_health": 100.0
    }
    mocker.patch("inference.reset_environment", return_value=dummy_obs)
    mocker.patch("inference.get_action", return_value="monitor")
    mocker.patch("inference.requests.post", side_effect=Exception("API Error"))

    mock_log_step = mocker.patch("inference.log_step")
    mock_log_end = mocker.patch("inference.log_end")
    mocker.patch("inference.log_start")

    # Run the episode
    run_episode("dummy_task")

    # Verify log_step was called with the fallback values exactly as expected
    mock_log_step.assert_called_once_with(
        step=1,
        action="monitor",
        reward=0.01,
        done=True,
        error="API Error"
    )

    # Verify log_end was called indicating episode end due to done=True
    mock_log_end.assert_called_once()
