"""
calminerva.exporters
--------------------

    Functions to export courses to various formats.
"""
from datetime import datetime
import icalendar
import pytz

UTC = pytz.utc
STAMP = datetime.now(UTC)


def ics(events):
    """
    Export events to iCalendar (.ics) format.

    Returns
    -------
    bytes
        Complete RFC-5545 compliant iCalendar content.
    """
    def ics_recurrence_rule(until):
        return dict(FREQ='WEEKLY', UNTIL=until)

    def generate_ics_event(event):
        ics_event = icalendar.Event()
        ics_event.add('summary', event.summary)
        ics_event.add('description', event.description)
        ics_event.add('location', event.location)
        ics_event.add('dtstart', event.start.astimezone(UTC))
        ics_event.add('dtend', event.end.astimezone(UTC))
        ics_event.add('dtstamp', STAMP)
        ics_event.add('rrule', ics_recurrence_rule(event.until))
        return ics_event

    cal = icalendar.Calendar()
    cal.add('prodid', '-//Minerva Schedule Exporter//EN')
    cal.add('version', '2.0')

    for event in events:
        ics_event = generate_ics_event(event)
        cal.add_component(ics_event)

    return cal.to_ical()


def gcal(events):
    """
    Export events to Google Calendar format.

    Exporting to Google Calendar actually requires authentication. This
    function only implements event-processing such that the returned events
    can be inserted in a Google Calendar through OAuth2.

    Yields
    ------
    dict
        Event resources compatible with Google Calendar API.
    """
    def gcal_date(dt):
        dt_utc = dt.astimezone(UTC)
        return {
            'dateTime': dt_utc.isoformat(),
            'timeZone': dt_utc.tzinfo.zone}

    def gcal_recurrence_rule(until):
        until = icalendar.prop.vDatetime(until).to_ical().decode()
        rrule = 'RRULE:FREQ=WEEKLY;UNTIL={}'.format(until)
        return {'rrule': [rrule]}

    def generate_gcal_event(event):
        gcal_event = {}
        gcal_event['summary'] = event.summary
        gcal_event['description'] = event.description
        gcal_event['location'] = event.location
        gcal_event['start'] = gcal_date(event.start)
        gcal_event['end'] = gcal_date(event.end)
        gcal_event['recurrence'] = gcal_recurrence_rule(event.until)
        return gcal_event

    for event in events:
        yield generate_gcal_event(event)
