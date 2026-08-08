import pytest
from enterprise_ai_api.agents.retry import MAX_TOOL_ATTEMPTS, RetryPolicy


def test_retry_policy_defaults_to_one_attempt() -> None:
    assert RetryPolicy().max_attempts == 1


@pytest.mark.parametrize("max_attempts", [0, MAX_TOOL_ATTEMPTS + 1])
def test_retry_policy_rejects_out_of_bounds_attempts(max_attempts: int) -> None:
    with pytest.raises(ValueError, match="max_attempts must be between"):
        RetryPolicy(max_attempts=max_attempts)
