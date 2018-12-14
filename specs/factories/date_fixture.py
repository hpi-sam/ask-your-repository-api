"""Manages uuids for tests in one file"""
DATES = [
    "2018-12-10T22:28:53+00:00",
    "2018-12-11T22:28:53+00:00",
    "2018-12-12T22:28:53+00:00",
    "2018-12-13T22:28:53+00:00"]

def get_date(index):
    """get a date, each index will be a new date.
    All dates are 1 day after each other"""
    return DATES[index]
