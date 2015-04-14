This schedule generator is built on Python 2.7, with dependencies on the following libraries:
* Astral from pypi.python.org (use "pip install astral"), to determine times of day
* convertdate available (use "pip install convertdate") to convert between different calendar systems
* docx (experimental, not working yet -- use "pip install docx") for Word file generation 
* win32com (http://sourceforge.net/projects/pywin32/files/) for OLE Word controls to generate Word file
* arrow (use "pip install arrow") to determine DST

The following components are used:
* calendar.py: Build a list of holidays for the given Jewish year / month
* times.py: Calculate relevant times per day for each holiday
* ole.py: Helper library to build a document using Win32 OLE
* schedule.py: Main driver to create monthly schedule