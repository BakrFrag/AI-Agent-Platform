import datetime
from zoneinfo import ZoneInfo

cairo_tz = ZoneInfo('Africa/Cairo')

def get_cairo_time():
    """Get current datetime in Cairo timezone using zoneinfo"""
    return datetime.datetime.now(cairo_tz)