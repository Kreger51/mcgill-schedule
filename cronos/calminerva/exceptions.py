"""
calminerva.exceptions
--------------------

Package-specific exceptions.
"""


class MinervaCalendarError(Exception):
    """
    Base exception class. All Minerva-specific expections should subclass
    this exception.
    """
    pass


class LoginError(MinervaCalendarError):
    """
    Raised when the Minerva login information is incorrect.
    """
    pass


class SemesterError(MinervaCalendarError):
    """
    Raised when the user is not registered for the requested semester. This
    implies that it is valid, however.
    """
    pass

class UselessCourse(MinervaCalendarError):
    """
    Raised when a row in a course meeting time listing starts and ends on the
    same day or when time is TBA. Used to control flow during parse.
    """
    pass
