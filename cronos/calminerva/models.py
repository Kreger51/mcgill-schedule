"""
calminerva.models
---------------

Models for the Minerva scraper/exporter.
"""
from collections import namedtuple

MODELS = ['Course', 'Event']


date_fields = ['start', 'end', 'until']
format_fields = ['code',  'instructor', 'section', 'title', 'type']
_misc_fields = ['group', 'location']
_course_fields = set(date_fields + format_fields + _misc_fields)
Course = namedtuple('Course', sorted(_course_fields))
Course.__doc__ += """
A single-day course.

A Course Section with lectures on Monday and Wednesday is represented
by two `Course`s.

The `start` and `end` fields encapsulate both the first day this course
occurs on as well as the start and end times.

`group` is used to optionally group similar courses.
============  ===================================
Field         Example
============  ===================================
code          FACC 300
end           datetime.datetime(2014, 1, 8, 17, 25)*
instructor    Raad Jassim
location      Macdonald Harrington Building G-10
section       001
start         datetime.datetime(2014, 1, 8, 16, 5)*
title         Engineering Economy
type          Lecture
until         datetime.datetime(2014, 4, 11, 17, 25)*
============  ===================================
*ALL datetimes should be aware.
"""


_formatted_fields = ['summary', 'description']
Formatter = namedtuple('Formatter', _formatted_fields)
Formatter.__doc__ += """
Formatter for the summary and description event properties.

Attributes are format strings which may use keyword replacement fields like
`str.format()`. Fields can be any field in `format_fields`.
"""

default_formatter = Formatter(
    summary='{code} - {type[0]}',
    description='{title} - {section}\n{instructor}'
)


_event_fields = set(date_fields + _misc_fields + _formatted_fields)
Event = namedtuple('Event', sorted(_event_fields))


def _make_event(course, formatter):
    def format(course, format_string):
        return format_string.format(**course._asdict())
    d = {}
    for k in _formatted_fields:
        d[k] = format(course, getattr(formatter, k))
    for k in _event_fields.intersection(_course_fields):
        d[k] = getattr(course, k)
    return Event(**d)


def events(courses, formatter):
    """
    Helper function to generate events from courses and a formatter.
    """
    return [_make_event(c, formatter) for c in courses]
