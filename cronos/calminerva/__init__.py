"""
Minerva Schedule Scraper
------------------------

    Basic usage:
    >>> import os
    >>> import cronos.calminerva as calminerva
    >>> user = os.environ['MINERVA_USER']
    >>> secret = os.environ['MINERVA_SECRET']
    >>> season = 'fall'
    >>> year = 2014
    >>> courses = calminerva.from_minerva(user, secret, season, year)
    >>> first_course = courses[0]

    You can also scrape the HTML directly:
    >>> with open('winter_2014.html') as f:
    ...     courses2 = calminerva.from_html(f)

    `Course`s contain all the data necessary to generate calendar events
    via custom formatters:
    >>> formatter = calminerva.Formatter('{code}', '{title}\\n{instructor}')
    >>> events = calminerva.events(courses, formatter)

    See `Formatter` for available fields.

    Events and courses are JSON serializable and deserializable:
    >>> from cronos.calminerva import load, dump, Course, Event
    >>> assert courses == load_models(dump(courses), model=Course)
    >>> assert events == load_models(dump(events), model=Event)

    Finally, events can be exported like so:
    >>> ics = calminerva.ics(events)
    >>> gcal_events = calminerva.gcal(events)
"""
from .models import Formatter, Event, Course, default_formatter, events
from .scraper import SEASONS, from_minerva, from_html
from .serial import load, load_models, dump, pretty_dump
from .exporters import ics, gcal

