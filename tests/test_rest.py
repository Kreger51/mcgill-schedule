import difflib
import functools
import pytest
import json

from cronos import calminerva
from .conftest import w14_html


def assert_response(r):
    try:
        assert r.status_code < 400
    except AssertionError:
        print(r.data)
        raise




@pytest.fixture(scope='module')
def w14_courses(w14_html):
    return calminerva.from_html(w14_html)


@pytest.fixture(scope='module')
def w14_events(w14_courses):
    return calminerva.events(w14_courses, calminerva.default_formatter)



@pytest.fixture(scope='module')
def post(app):
    return functools.partial(app.post, content_type='application/json')


def response_to_model(response, k, model):
    d = calminerva.load(response.data.decode())
    d = d[k]
    return calminerva.load_models(d, model, False)


def test_events_no_events(post):
    formatter = calminerva.Formatter('{code}', '{instructor}')
    r = post('/events', data=calminerva.dump({'formatter': formatter}))
    assert r.status_code == 400


def test_events(post, w14_courses):
    formatter = calminerva.Formatter('{code}', '{instructor}')
    r = post(
        '/events',
        data=calminerva.dump({
            'courses': w14_courses,
            'formatter': formatter
        })
    )
    assert_response(r)
    events = response_to_model(r, 'events', calminerva.Event)
    assert events == calminerva.events(w14_courses, formatter)


def test_events_no_formatter(post, w14_courses, w14_events):
    r = post(
        '/events',
        data=calminerva.dump({
            'courses': w14_courses
        })
    )
    assert_response(r)
    events = response_to_model(r, 'events', calminerva.Event)
    assert events == w14_events


def test_calendar_gcal(post, w14_events):
    r = post(
        '/calendar',
        data=calminerva.dump({
            'events': w14_events,
            'format': 'gcal'
        })
    )
    assert_response(r)
    data = json.loads(r.data.decode())
    gcal_events = data['events']
    for r, e in zip(gcal_events, calminerva.gcal(w14_events)):
        assert r == e


def test_calendar_ics(post, w14_events):
    r = post(
        '/calendar',
        data=calminerva.dump({
            'events': w14_events,
            'format': 'ics'
        })
    )
    assert_response(r)
    data = json.loads(r.data.decode())
    calendar = data['calendar']
    expected = calminerva.ics(w14_events).decode()
    try:
        assert calendar == expected
    except AssertionError:
        # diff = difflib.context_diff(calendar, expected)
        print(calendar)
        print(expected)
        # for line in diff:
            # print(line)
        raise
