from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar, Dict, Optional, Generic
import traceback

T = TypeVar('T')


class Maybe(Generic[T]):
    def __init__(self, value: object = None, contains_value: bool = True):
        self.value = value
        self.contains_value = contains_value

    def __bool__(self):
        if self.contains_value:
            return True
        return False

    def bind(self, f: Callable) -> Maybe[T]:
        if not self.contains_value:
            return Maybe(None, contains_value=False)
        try:
            result = f(self.value)
            return Maybe(result)
        except:
            return Maybe(None, contains_value=False)


class Success(Generic[T]):
    def __init__(self, value: T = None, error_status: Dict = None):
        self.value = value
        self.error_status = error_status

    def __bool__(self):
        if self.error_status:
            return False
        return True

    def get_error_message(self) -> Optional[str]:
        if self.error_status:
            return self.error_status['exc'].message
        return None

    def bind(self, f: Callable, *args, **kwargs) -> Success[T]:
        if self.error_status:
            return Success(None, error_status=self.error_status)
        try:
            result = f(self.value, *args, **kwargs)
            return Success(result)
        except Exception as e:
            failure_status = {
                'trace': traceback.format_exc(),
                'exc': e,
                'args': args,
                'kwargs': kwargs
            }
            return Success(None, error_status=failure_status)
