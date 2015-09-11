"""
calminerva.utils
----------------

Simple utilities.
"""


def max_start_date(courses):
    """
    Identify the maximum start date amongst all courses.
    """
    return max([c.start for c in courses])
