

from typing import Optional, TypeVar


T = TypeVar("T")
def none_check(value: Optional[T]) -> T:
    assert value is not None, "Expected value to not be None"
    return value