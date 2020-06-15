import itertools
from collections import deque
from typing import Deque

from pandas import Series


class History:
    """ stores previous recommendations, and enables filtering out too recent ones. """

    history: Deque = deque(maxlen=0)

    @classmethod
    def set_maxlen(cls, maxlen: int) -> None:
        if maxlen != cls.history.maxlen:
            h = deque(cls.history, maxlen)

    @classmethod
    def append(cls, item):
        cls.history.append(item)

    @classmethod
    def filter(cls, items: Series) -> Series:
        return items.drop(itertools.chain.from_iterable(cls.history), errors='ignore')
