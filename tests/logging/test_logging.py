from typing import List
import pytest
from locast.logging_functions import log_progress


def test_log_progress_prints_correctly(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # given
    total = 5
    name = "candles"
    action = "stored"
    emoji = "📀"

    market = "BTC-USD"

    result: List[str] = []

    # when
    for done in range(1, total + 1):
        log_progress(emoji, market, name, action, done, total)
        out, _ = capsys.readouterr()
        result.append(out)

    print(result)

    # then
    expected: List[str] = []
    for done in range(1, total + 1):
        msg = f"📀 {done} of {total} {market}-{name} {action}.\r"
        expected.append(msg)

    expected[-1] = f"\r📀 {total} of {total} {market}-{name} {action}. ✅\n"

    assert result == expected
