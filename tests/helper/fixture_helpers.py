from typing import Type, TypeVar

import pytest


T = TypeVar("T")


def get_typed_fixture(
    request: pytest.FixtureRequest,
    fixture_name: str,
    fixture_type: Type[T],
) -> T:
    value = request.getfixturevalue(fixture_name)
    assert isinstance(value, fixture_type)
    return value
