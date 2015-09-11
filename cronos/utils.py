from datetime import datetime


def max_start_date(courses):
    """
    Identify the maximum start date amongst all courses.

    Returns
    -------
    ISO8601 date string
    """
    return max([c.start for c in courses]).date().isoformat()


def this_and_next_year():
    current_year = datetime.now().year
    return [x for x in (current_year, current_year + 1)]
