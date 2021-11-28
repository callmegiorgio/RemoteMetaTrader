import pytz
from datetime import datetime, timedelta
from unittest import TestCase
from rmt      import timezone

class TestTimezone(TestCase):
    def test_creates_plain_pytz_timezone_on_zero_offset(self):
        tz = timezone('EET', timedelta(0))

        self.assertEquals(tz, pytz.timezone('EET'))

    def test_creates_timezone_on_positive_offset(self):
        # 2021-03-14 09:30:00
        dt = datetime(2021, 3, 14, 9, 30)
        
        ny_tz = pytz.timezone('America/New_York')
        ny_dt = ny_tz.localize(dt)

        ny_plus_7h_tz = timezone('America/New_York', timedelta(hours=7))
        offset_dt     = ny_dt.astimezone(ny_plus_7h_tz)

        # 2021-03-14 16:30:00
        self.assertEquals(offset_dt.year,   2021)
        self.assertEquals(offset_dt.month,  3)
        self.assertEquals(offset_dt.day,    14)
        self.assertEquals(offset_dt.hour,   16)
        self.assertEquals(offset_dt.minute, 30)
        self.assertEquals(offset_dt.second, 0)

    def test_creates_timezone_on_negative_offset(self):
        # 2021-03-14 01:40:20
        dt = datetime(2021, 3, 14, 1, 40, 20)
        
        helsinki_tz = pytz.timezone('Europe/Helsinki')
        helsinki_dt = helsinki_tz.localize(dt)

        helsinki_minus_3h32m_tz = timezone('Europe/Helsinki', -timedelta(hours=3, minutes=32))
        offset_dt               = helsinki_dt.astimezone(helsinki_minus_3h32m_tz)

        # 2021-03-13 22:08:20
        self.assertEquals(offset_dt.year,   2021)
        self.assertEquals(offset_dt.month,  3)
        self.assertEquals(offset_dt.day,    13)
        self.assertEquals(offset_dt.hour,   22)
        self.assertEquals(offset_dt.minute, 8)
        self.assertEquals(offset_dt.second, 20)

    def test_creates_timezone_on_utc_offset(self):
        # 2021-06-20 07:45:44.2478
        dt = datetime(2021, 6, 20, 7, 45, 44, 2478)

        utc_dt = pytz.utc.localize(dt)

        utc_plus_12_tz = timezone('UTC', timedelta(hours=12))
        offset_dt      = utc_dt.astimezone(utc_plus_12_tz)

        # 2021-06-20 19:45:44.2478
        self.assertEquals(offset_dt.year,        2021)
        self.assertEquals(offset_dt.month,       6)
        self.assertEquals(offset_dt.day,         20)
        self.assertEquals(offset_dt.hour,        19)
        self.assertEquals(offset_dt.minute,      45)
        self.assertEquals(offset_dt.second,      44)
        self.assertEquals(offset_dt.microsecond, 2478)
