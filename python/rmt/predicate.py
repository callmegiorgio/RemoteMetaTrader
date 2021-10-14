from datetime import time, tzinfo
from typing   import Any, Callable
from rmt      import SlottedClass

Predicate = Callable[[Any], bool]
"""A predicate is an invocable type that takes one parameter of any type and returns a bool."""

TimePredicate = Callable[[time], bool]
"""Predicate that takes a `time` parameter."""

class AtTime(SlottedClass):
    """Checks whether a time is a specific time."""

    __slots__ = ['_time']

    def __init__(self, *args, **kwargs):
        self._time = time(*args, **kwargs)

    def __call__(self, t: time) -> bool:
        return self._time == t

class AfterTime(SlottedClass):
    """Checks whether a time occurs after (inclusive) a specific time."""

    __slots__ = ['_start_time']

    def __init__(self, *args, **kwargs):
        self._start_time = time(*args, **kwargs)

    def __call__(self, t: time) -> bool:
        return t >= self._start_time

class BeforeTime(SlottedClass):
    """Checks whether a time occurs before (inclusive) a specific time."""

    __slots__ = ['_stop_time']

    def __init__(self, *args, **kwargs):
        self._stop_time = time(*args, **kwargs)

    def __call__(self, t: time) -> bool:
        return t <= self._stop_time

class TimeRange(SlottedClass):
    """Checks whether a time occurs in a time range [start time, stop time)."""

    __slots__ = ['_start_time', '_stop_time']

    def __init__(self, start_time: time, stop_time: time):
        self._start_time = start_time
        self._stop_time  = stop_time

    def __call__(self, t: time) -> bool:
        if self._start_time <= self._stop_time:
            return t >= self._start_time and t < self._stop_time
        else:
            return t >= self._start_time or t < self._stop_time

class AtMinute(SlottedClass):
    """Checks whether a time occurs at a specific minute."""

    __slots__ = ['_time']

    def __init__(self, hour: int, minute: int, tzinfo: tzinfo = None):
        self._time = time(hour=hour, minute=minute, tzinfo=tzinfo)

    def __call__(self, t: time) -> bool:
        return self._time == t.replace(second=0, microsecond=0)

class AtHour(SlottedClass):
    """Checks whether a time occurs at a specific hour."""

    __slots__ = ['_time']

    def __init__(self, hour: int, tzinfo: tzinfo = None):
        self._time = time(hour=hour, minute=0, tzinfo=tzinfo)

    def __call__(self, t: time) -> bool:
        return self._time == t.replace(minute=0, second=0, microsecond=0)

class Count(SlottedClass):
    """Checks if a predicate is `True` for at most a number of times.
    
    `Count` is a predicate that takes a `count` and another predicate upon creation.
    An instance of `Count` evaluates to `True` while its underlying predicate also
    evaluates to `True` for at most `count` times. If the underlying predicate is
    `True` for more than `count` times, `Count` returns `False` until the underlying
    predicate is `False`, moment which `Count` is reset and the process is repeated.
    """

    __slots__ = ['_pred', '_count', '_counter']

    def __init__(self, pred: Predicate, count: int):
        if count < 0:
            raise ValueError("parameter 'count' of class {} may not be less than 0".format(self.__class__))

        self._pred  = pred
        self._count = count
        self._counter = 0
    
    def __call__(self, obj: Any) -> bool:
        if self._pred(obj):
            if self._counter == self._count:
                return False

            self._counter += 1

            return True
        else:
            self._counter = 0

            return False

class Once(Count):
    """Same as `Count(pred, 1)`. Added for semantics."""

    def __init__(self, pred: Predicate):
        super().__init__(pred, 1)