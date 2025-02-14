# -*- coding: utf-8 -*-
# Test data taken from http://www.timeanddate.com/sun/uk/london

import datetime

import freezegun
import pytest
from almost_equal import datetime_almost_equal

from astral import TimePeriod, sun
from astral.location import Location
from astral.sun import SunDirection


class TestGoldenHour:
    """Tests for the golden_hour function"""

    @pytest.mark.parametrize(
        "day,golden_hour",
        [
            (
                datetime.date(2015, 12, 1),
                (
                    datetime.datetime(2015, 12, 1, 1, 10, 10),
                    datetime.datetime(2015, 12, 1, 2, 0, 43),
                ),
            ),
            (
                datetime.date(2016, 1, 1),
                (
                    datetime.datetime(2016, 1, 1, 1, 27, 46),
                    datetime.datetime(2016, 1, 1, 2, 19, 1),
                ),
            ),
        ],
    )
    def test_morning(
        self, day: datetime.date, golden_hour: TimePeriod, new_delhi: Location
    ):
        start1 = golden_hour[0].replace(tzinfo=datetime.timezone.utc)
        end1 = golden_hour[1].replace(tzinfo=datetime.timezone.utc)

        start2, end2 = sun.golden_hour(new_delhi.observer, day, SunDirection.RISING)
        assert datetime_almost_equal(end1, end2, seconds=90)
        assert datetime_almost_equal(start1, start2, seconds=90)

    def test_evening(self, london: Location):
        test_data = {
            datetime.date(2016, 5, 18): (
                datetime.datetime(2016, 5, 18, 19, 2),
                datetime.datetime(2016, 5, 18, 20, 17),
            )
        }

        for day, golden_hour in test_data.items():
            start1 = golden_hour[0].replace(tzinfo=datetime.timezone.utc)
            end1 = golden_hour[1].replace(tzinfo=datetime.timezone.utc)

            start2, end2 = sun.golden_hour(london.observer, day, SunDirection.SETTING)
            assert datetime_almost_equal(end1, end2, seconds=60)
            assert datetime_almost_equal(start1, start2, seconds=60)

    @freezegun.freeze_time("2015-12-1")
    def test_no_date(self, new_delhi: Location):
        start = datetime.datetime(2015, 12, 1, 1, 10, 10, tzinfo=datetime.timezone.utc)
        end = datetime.datetime(2015, 12, 1, 2, 0, 43, tzinfo=datetime.timezone.utc)
        ans = sun.golden_hour(new_delhi.observer)
        assert datetime_almost_equal(ans[0], start, 90)
        assert datetime_almost_equal(ans[1], end, 90)


class TestBlueHour:
    """Tests for the blue_hour function"""

    def test_morning(self, london: Location):
        test_data = {
            datetime.date(2016, 5, 19): (
                datetime.datetime(2016, 5, 19, 3, 19),
                datetime.datetime(2016, 5, 19, 3, 36),
            )
        }

        for day, blue_hour in test_data.items():
            start1 = blue_hour[0].replace(tzinfo=datetime.timezone.utc)
            end1 = blue_hour[1].replace(tzinfo=datetime.timezone.utc)

            start2, end2 = sun.blue_hour(london.observer, day, SunDirection.RISING)
            assert datetime_almost_equal(end1, end2, seconds=90)
            assert datetime_almost_equal(start1, start2, seconds=90)

    def test_evening(self, london: Location):
        test_data = {
            datetime.date(2016, 5, 19): (
                datetime.datetime(2016, 5, 19, 20, 18),
                datetime.datetime(2016, 5, 19, 20, 35),
            )
        }

        for day, blue_hour in test_data.items():
            start1 = blue_hour[0].replace(tzinfo=datetime.timezone.utc)
            end1 = blue_hour[1].replace(tzinfo=datetime.timezone.utc)

            start2, end2 = sun.blue_hour(london.observer, day, SunDirection.SETTING)
            assert datetime_almost_equal(end1, end2, seconds=90)
            assert datetime_almost_equal(start1, start2, seconds=90)

    @freezegun.freeze_time("2016-5-19")
    def test_no_date(self, london: Location):
        start = datetime.datetime(2016, 5, 19, 20, 18, tzinfo=datetime.timezone.utc)
        end = datetime.datetime(2016, 5, 19, 20, 35, tzinfo=datetime.timezone.utc)
        ans = sun.blue_hour(london.observer, direction=SunDirection.SETTING)
        assert datetime_almost_equal(ans[0], start, 90)
        assert datetime_almost_equal(ans[1], end, 90)
