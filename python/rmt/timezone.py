import pytz
import pytz.tzinfo
from datetime import timedelta, tzinfo

def format_offset(offset: timedelta) -> str:
    hours, remainder = divmod(offset.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    hours   = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)

    if seconds:
        return '{}:{:02}:{:02}'.format(hours, minutes, seconds)
    elif minutes:
        return '{}:{:02}'.format(hours, minutes)
    else:
        return str(hours)

def dst_timezone(underlying_tz: pytz.tzinfo.DstTzInfo, offset: timedelta) -> tzinfo:
    """Creates a timezone based off a pytz DST timezone and a time offset."""

    # Pytz DST timezones have subclasses deriving from pytz.tzinfo.DstTzInfo for
    # each DST timezone. Each subclass implements three class variables:
    # 1. `zone`, a string for the zone name;
    # 2. `_utc_transition_times`, list of datetimes in which DST is applied;
    # 3. `_transition_info`, list of transition data for each entry in the above list.
    #
    # We don't change `_utc_transition_times` to create an offset timezone, since
    # it tells us the times when the transition occurs in the underlying timezone.
    # What we do is change the first member of a `_transition_info` tuple that
    # stores the UTC offset by adding our own `offset` to it, and then subclass
    # DstTzInfo with a new `_transition_info`.
    #
    # `zone` is also changed so that printing the timezone will show it's an offset
    # timezone. For example, 'America/New_York' with an offset of 7 hours will be
    # printed as 'America/New_York+7'.

    transition_info = underlying_tz._transition_info.copy()

    for i, t in enumerate(transition_info):
        utcoffset, dst, tzname = t
        transition_info[i] = (utcoffset + offset, dst, tzname)

    class OffsetDstTzInfo(pytz.tzinfo.DstTzInfo):
        zone = '{}+{}'.format(underlying_tz.zone, format_offset(offset))

        _utc_transition_times = underlying_tz._utc_transition_times
        _transition_info 	  = transition_info

    return OffsetDstTzInfo()

def static_timezone(underlying_tz: pytz.tzinfo.StaticTzInfo, offset: timedelta) -> tzinfo:
    """Creates a timezone based off a pytz static timezone and a time offset."""

    class OffsetStaticTzInfo(pytz.tzinfo.StaticTzInfo):
        zone = '{}+{}'.format(underlying_tz.zone, format_offset(offset))

        _utcoffset = underlying_tz._utcoffset + offset
        _tzname    = underlying_tz._tzname

    return OffsetStaticTzInfo()

def timezone(zone: str, offset: timedelta) -> tzinfo:
    """Creates a pytz timezone with a time offset.
    
    >>> dt = datetime(2021, 3, 14, 9, 30)
    >>> ny_tz = pytz.timezone('America/New_York')
    >>> ny_dt = ny_tz.localize(dt)
    >>> repr(ny_dt)
    datetime.datetime(2021, 3, 14, 9, 30, tzinfo=<DstTzInfo 'America/New_York' EDT-1 day, 20:00:00 DST>)
    >>> ny_plus_7h_tz = timezone('America/New_York', timedelta(hours=7))
    >>> ny_dt.astimezone(ny_plus_7h_tz)
    datetime.datetime(2021, 3, 14, 16, 30, tzinfo=<DstTzInfo 'America/New_York+7' EDT+3:00:00 DST>)
    
    Parameters
    ----------
    zone : str
        A valid pytz zone string.
    
    offset : timedelta
        Time to offset the timezone.

    Raises
    ------
    Propagates any exception raised by `pytz.timezone()`.

    Returns
    -------
    A `tzinfo` object representing the offset timezone.
    """

    underlying_tz = pytz.timezone(zone)

    if offset == timedelta(0):
        return underlying_tz

    if isinstance(underlying_tz, pytz.tzinfo.DstTzInfo):
        return dst_timezone(underlying_tz, offset)
    else:
        return static_timezone(underlying_tz, offset)