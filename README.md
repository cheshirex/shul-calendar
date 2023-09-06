This schedule generator is built on Python 3.9

The following components are used:
* calendar.py: Build a list of holidays for the given Jewish year / month
* times.py: Calculate relevant times per day for each holiday
* ole.py: Helper library to build a document using Win32 OLE
* schedule.py: Main driver to create monthly schedule

To run:
`python schedule.py <hebrew year> <hebrew month number>`
