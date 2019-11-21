import datetime
from distutils.version import LooseVersion

# for the ww release format:
today = datetime.datetime.today()
year, week, day = today.isocalendar()
year_work_week = "{0}{1}".format(year-2000, week)

# MAJOR ----------
# 0 = beta/alpha code
# incremented any time you change the API that may break backwards compatibility
# in a fairly major way
MAJOR = 0
# MINOR ------------
# recommend using datetime info to show last update as part of versiona
# but the other option is to manually rev, and put the revision in the build
MINOR = 5
# BUILD ------
# either make this a manual number to increment or use the SVN revision
BUILD = 1
__version__ = LooseVersion("{major}.{minor}.{build}".format(
                major=MAJOR,
                minor=MINOR,
                build=BUILD, ))
