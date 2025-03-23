from multiprocessing.sharedctypes import Value
from typing import Any, Generic, TypeVar
from hearsay.exceptions import RequestError

IT = TypeVar('IT')
"""A generic wrapper to make its nested value mutable, and to indicate an argument which must be set before control is returned."""
class OutVar(Generic[IT]):
    def __init__(self, default = None):
        self._result = default

    @property
    def result(self):
        if self._result == None:
            raise RequestError("An OutVar argument wasn't set.")
        return self._result

    @result.setter
    def result(self, value:IT):
        self._result = value

    @property
    def has_been_set(self) -> bool:
        return self._result != None
