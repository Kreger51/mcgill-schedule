"""
calminerva.scraper
------------------

Functions to scrape Minerva.
"""
import bs4
import requests
from datetime import datetime, timedelta
import pytz

from .exceptions import UselessCourse, LoginError, SemesterError
from .models import Course


# Build required URLS
_url_base = 'https://horizon.mcgill.ca/pban1/%s'
urls = {'login': 'twbkwbis.P_ValLogin',
        'schedule': 'bwskfshd.P_CrseSchdDetl'}
urls = {k: _url_base % v for k, v in urls.items()}
# Semester map (human -> request)
SEASONS = ['fall', 'winter', 'summer']
season_labels = ['09', '01', '05']
season_map = {k: v for k, v in zip(SEASONS, season_labels)}

LT = pytz.timezone('America/New_York')
WEEKDAY_MAPPING = dict(M=0, T=1, W=2, R=3, F=4)


def _format_date(date):
    fmt = "%b %d, %Y"
    return datetime.strptime(date, fmt).date()


def _format_time(time):
    fmt = "%I:%M %p"
    return datetime.strptime(time, fmt).time()


def _next_weekday(d, weekday):
    """
    Find first date for the first given weekday after given date.

    Lookup is inclusive, meaning that if `d` is on a Tuesday and `weekday`
    also corresponds to Tuesday, the returned value is the same as the input
    date.

    Parameters
    ----------
    d : datetime.date
        Date after which to look for weekday.
    weekday : int
        Given weekday.
        0 = Monday, 1 = Tuesday ...

    Returns
    -------
    datetime.date
    """
    days_ahead = weekday - d.weekday()
    # Target day already happened this week
    if days_ahead < 0:
        days_ahead += 7
    return d + timedelta(days_ahead)


def _make_course(*, caption, date_range, day, instructor, location,
                 time_range, _type, group=1):
    """
    Make a `Course` from raw course info (obtained from parsing HTML).

    All input parameters are strings. All dates in `Course` are localized.
    See below for example.

    Returns
    -------
    calmcgill.Course

    Example
    -------
    See tests
        >>> course = _make_course(
        ... caption='Engineering Economy. - FACC 300 - 001',
        ... date_range='Jan 06, 2014 - Apr 11, 2014',  #  Jan 06 is a Monday
        ... day='W', instructor='Raad Jassim' ,
        ... location='Macdonald Harrington Building G-10',
        ... time_range='4:05 PM - 5:25 PM', _type='Lecture')
        >>> print(course) #doctest: +ELLIPSIS
        Course(code='FACC 300',\
 end=datetime.datetime(2014, 1, 8, 17, 25, tzinfo=...),\
 group=1,\
 instructor='Raad Jassim',\
 location='Macdonald Harrington Building G-10',\
 section='001',\
 start=datetime.datetime(2014, 1, 8, 16, 5, tzinfo=...),\
 title='Engineering Economy',\
 type='Lecture',\
 until=datetime.datetime(2014, 4, 11, 17, 25, tzinfo=...)\
)
    """
    def aware_combine(date, time):
        return LT.localize(datetime.combine(date, time), is_dst=None)

    course = {}  # Store only relevant values in this.
    dates = date_range.split(' - ')
    if dates[0] == dates[1] or time_range == 'TBA':
        raise UselessCourse

    # Make datetime values
    first_date, until_date = [_format_date(date) for date in dates]
    day = WEEKDAY_MAPPING[day]
    start_date = _next_weekday(first_date, day)
    times = time_range.split(' - ')
    start_time, end_time = [_format_time(time) for time in times]
    course['start'] = aware_combine(start_date, start_time)
    course['end'] = aware_combine(start_date, end_time)
    course['until'] = aware_combine(until_date, end_time)

    # Make string values
    title, course['code'], course['section'] = caption.split(' - ')
    course['title'] = title.rstrip('.')
    course['instructor'] = instructor.rstrip()
    course['location'] = location
    course['type'] = _type
    course['group'] = group
    return Course(**course)


def parse(html):
    """
    Parse 'Minerva schedule' HTML document.

    Parameters
    ----------
    html : str
        Raw 'Student Schedule by Course Section' HTML.

    Returns
    -------
    list of `Course`s
    """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    tables = soup.select('.datadisplaytable')
    # Split tables into (detail, meeting time) course pairs
    course_pairs = zip(tables[::2], tables[1::2])
    meeting_time_keys = ('time_range', 'days', 'location', 'date_range',
                         '_type', 'instructor')
    courses = []
    group_registry = {}
    group_counter = 1
    for detail, meeting_time in course_pairs:
        meeting_rows = meeting_time.select('tr')
        # A meeting time table may have more than one meeting row
        for meeting_row in meeting_rows[1:]:  # First row is only headers
            raw = {}
            caption = detail.select('caption')[0].get_text()
            raw['caption'] = caption
            values = (x.get_text() for x in meeting_row.select('td'))
            raw.update(dict(zip(meeting_time_keys, values)))

            # Assign ID
            title = caption.split('-', 1)[0]
            val = group_registry.setdefault(title, group_counter)
            if val != group_counter:
                raw['group'] = val
            else:
                raw['group'] = group_counter
                group_counter += 1

            days = raw.pop('days')
            for day in days:
                try:
                    course = _make_course(day=day, **raw)
                except UselessCourse:
                    pass
                else:
                    courses.append(course)
    return courses


def fetch(user, secret, season, year):
    """
    Login to Minerva and fetch schedule.

    Attributes
    ----------
    user : str
        Either McGill ID Number of McGill Username
    secret : str
        Either Minerva PIN or McGill Password, depending on `user`.
    season : {'fall', 'winter', 'summer'}, case-insensitive
        Season for which to fetch schedule.
    year : {int, str}
        Year for which to fetch schedule.

    Returns
    -------
    str
        'Schedule by Course Section' HTML document.

    Raises
    ------
    KeyError
        Input `season` not in list of valid seasons.
    LoginError
        The `user`/`secret` combination is invalid.
    SemesterError
        The user is not registered for the requested season/year,
        i.e. semester, combination.
    """
    season = season.lower()
    try:
        month = season_map[season]
    except KeyError:
        msg = "Season '{:s}' not valid.\n".format(season)
        msg += "List of seasons: {}".format(list(SEASONS))
        raise KeyError(msg)
    term = "{}{}".format(year, month)
    login_data = {'sid': user, 'PIN': secret}
    term_data = {'term_in': term}
    with requests.Session() as session:
        session.get(urls['login'])
        r = session.post(urls['login'], data=login_data)
        if 'Authorization Failure' in r.text:
            raise LoginError
        r = session.post(urls['schedule'], data=term_data)
        if 'You are not currently registered for the term.' in r.text:
            raise SemesterError
        return session.get(urls['schedule']).text


from_html = parse


def from_minerva(user, secret, season, year):
    return from_html(fetch(user, secret, season, year))
