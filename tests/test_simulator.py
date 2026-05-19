import pytest
from unittest.mock import patch
from server.app import NetworkSimulator
from server.models import Observation

def test_network_simulator_step():
    sim = NetworkSimulator()

    # We patch random to make the test deterministic
    with patch("random.uniform", side_effect=lambda a, b: a), \
         patch("random.randint", side_effect=lambda a, b: a):

        sim.reset("task_2_medium")
        assert sim.step_count == 0

        # Test 1: Action normalization (whitespace, case) and basic step transition
        # " RATE_LIMIT  " -> "rate_limit"
        obs, reward, done, info = sim.step(" RATE_LIMIT  ")
        assert info["mitigation_applied"] == "rate_limit"
        assert sim.step_count == 1
        assert done is False
        assert sim.false_positives == 1
        assert info["is_attack_phase"] is False
        assert isinstance(obs, Observation)

        # Test 2: Invalid action defaults to "monitor"
        # At step_count=2, task_2_medium attack phase starts
        obs, reward, done, info = sim.step("invalid_action")
        assert info["mitigation_applied"] == "monitor"
        assert sim.step_count == 2
        assert info["is_attack_phase"] is True

        # Test 3: Valid action "block" during attack phase
        obs, reward, done, info = sim.step("block")
        assert info["mitigation_applied"] == "block"
        assert sim.step_count == 3
        assert info["is_attack_phase"] is True

        # Test 4: End of episode detection
        # fast forward to max_steps - 1
        sim.step_count = sim.max_steps - 1
        obs, reward, done, info = sim.step("monitor")
        assert done is True
        assert sim.step_count == sim.max_steps
