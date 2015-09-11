import datetime  # Needed for eval()
import difflib
import doctest
import functools
import os
import pytest
import shutil

from cronos.calminerva.exceptions import *
from cronos.calminerva.scraper import _make_course, parse, fetch, _next_weekday
from cronos.calminerva.scraper import LT, from_minerva
from cronos.calminerva.models import Course

from .conftest import login, w14_path, w14_html, w14_info, TEST_PATH

################################################################################
##                                  Scraper                                   ##
################################################################################
@pytest.fixture
def a_day():
    return datetime.date(2011, 7, 2)


def test_next_weekday_same_day(a_day):
    next_day = _next_weekday(a_day, a_day.weekday())
    assert a_day == next_day


def test_next_weekday_after(a_day):
    weekday = a_day.weekday() + 2
    next_day = _next_weekday(a_day, weekday)
    assert next_day == datetime.date(2011, 7, 4)


def test_next_weekday_before(a_day):
    weekday = a_day.weekday() - 1
    next_day = _next_weekday(a_day, weekday)
    assert next_day == datetime.date(2011, 7, 2 + 6)


@pytest.fixture
def dummy_raw(scope='function'):
    raw = dict(
        caption='Engineering Economy. - FACC 300 - 001',
        date_range='Jan 06, 2014 - Apr 11, 2014',  # Jan 06 is a Monday
        day='W',
        instructor='Raad Jassim',
        location='Macdonald Harrington Building G-10',
        time_range='4:05 PM - 5:25 PM',
        _type='Lecture',
        )
    return raw


def test_make_useless_course_tba(dummy_raw):
    dummy_raw['time_range'] = 'TBA'
    with pytest.raises(UselessCourse):
        _make_course(**dummy_raw)


def test_make_useless_course_start_is_end(dummy_raw):
    dummy_raw['date_range'] = 'Jan 06, 2014 - Jan 06, 2014'
    with pytest.raises(UselessCourse):
        _make_course(**dummy_raw)


@pytest.fixture(scope='function')
def courses(request):
    """
    Helper decorator to parse HTML from wrapped function's filename.
    """
    filename = request.function.__name__[5:]
    html_path = os.path.join(TEST_PATH, filename + '.html')
    html_doc = open(html_path).read()
    return parse(html_doc)


def test_one_course_one_day(courses):
    assert len(courses) == 1
    course = courses[0]
    assert course.start == LT.localize(datetime.datetime(2014, 9, 2, 18, 5))
    assert course.end == LT.localize(datetime.datetime(2014, 9, 2, 20, 55))
    assert course.until == LT.localize(datetime.datetime(2014, 12, 3, 20, 55))
    assert course.instructor == 'Mahdi Arian Nik'
    assert course.location == 'Macdonald Engineering Building 267'
    assert course.code == 'MECH 530'
    assert course.title == 'Mechanics of Composite Materials'
    assert course.section == '002'
    assert course.type == 'Lecture'
    assert course.group == 1


def test_one_course_two_days_diff_time(courses):
    assert len(courses) == 2
    a, b = courses
    unequal_fields = ['start', 'end', 'until']
    equal_fields = [k for k in a._fields if k not in unequal_fields]
    for field in equal_fields:
        x, y = getattr(a, field), getattr(b, field)
        try:
            assert x == y
        except AssertionError:
            print("Assertion -- Field = {}".format(field))
            raise
    for field in unequal_fields:
        x, y = getattr(a, field), getattr(b, field)
        try:
            if field is not 'until':
                assert x.date() != y.date()
            else:
                assert x.date() == y.date()
            assert x.time() != y.time()
        except AssertionError:
            print("Assertion -- Field = {}".format(field))
            raise

def test_one_course_two_days_same_time(courses):
    assert len(courses) == 2
    a, b = courses
    unequal_fields = ['start', 'end']
    equal_fields = [k for k in a._fields if k not in unequal_fields]
    for field in equal_fields:
        x, y = getattr(a, field), getattr(b, field)
        try:
            assert x == y
        except AssertionError:
            print("Assertion -- Field = {}".format(field))
            raise

    for field in unequal_fields:
        x, y = getattr(a, field), getattr(b, field)
        try:
            if field is not 'until':
                assert x.date() != y.date()
            else:
                assert x.date() == y.date()
            assert x.time() == y.time()
        except AssertionError:
            print("Assertion -- Field = {}".format(field))
            raise


def test_start_is_end_course(courses):
    assert courses == []


def test_tba_course(courses):
    assert courses == []


def test_two_courses_two_days(courses):
    unique_groups = set([course.group for course in courses])
    assert len(courses) == 4
    assert len(unique_groups) == 2


def test_one_course_tutorial_lecture(courses):
    unique_groups = set([course.group for course in courses])
    assert len(courses) == 2
    assert len(unique_groups) == 1


def test_invalid_season(login):
    user_id, password = login
    with pytest.raises(KeyError):
        fetch(user_id, password, 'spring', 2014)


def test_invalid_login():
    user_id, password = ['foo', 'bar']
    with pytest.raises(LoginError):
        fetch(user_id, password, 'winter', 2014)


def test_invalid_semester(login):
    user_id, password = login
    with pytest.raises(SemesterError):
        fetch(user_id, password, 'fall', 2050)


def test_winter_2014_runtime(w14_info):
    assert from_minerva(*w14_info)

################################################################################
##                                 Exporters                                  ##
################################################################################
@pytest.fixture
def dummy_course():
    date = functools.partial(datetime.datetime, tzinfo=LT)
    return Course(code='FACC 300',
                  end=date(2014, 1, 8, 17, 25),
                  instructor='Raad Jassim',
                  location='Macdonald Harrington Building G-10',
                  section='001',
                  start=date(2014, 1, 8, 16, 5),
                  title='Engineering Economy',
                  type='Lecture',
                  until=date(2014, 4, 11, 17, 25),
                  group=1,
    )


################################################################################
##                                  Doctest                                   ##
################################################################################

def test_docs(w14_html):
    filename = os.path.basename(w14_path)
    shutil.copy(w14_path, '.')
    import cronos.calminerva
    import cronos.calminerva.scraper
    f, _ = doctest.testmod(cronos.calminerva)
    f2, _ = doctest.testmod(cronos.calminerva.scraper)
    assert f == 0
    assert f2 == 0
    os.remove(filename)
