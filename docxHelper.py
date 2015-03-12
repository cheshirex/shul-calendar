#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from docx import Document
#from docx.shared import Inches

def addEntry(cells, offset, name, time=None):
	if name == None:
		# Special case -- merge this cell with the preceding and following cell
		return
	if isinstance(name, basestring):
		name = {'text': name}
	if 'bold' in name and name['bold']:
		pass
	if time:
		if isinstance(time, basestring):
			time = {'text': time}
		cells[0+offset].text = name['text']
		cells[0+offset].paragraphs[0].runs[0].rtl = True
		cells[1+offset].text = time['text']
		cells[1+offset].paragraphs[0].runs[0].rtl = True
	else:
		cells[0+offset].text = name['text'] # Need to figure out how to span multiple columns
		cells[0+offset].paragraphs[0].runs[0].rtl = True

def createTable(worddoc, rows, cols):
	return worddoc.add_table(rows=rows, cols=cols)
	
# For now, hardcoded to four columns
def createPopulateTable(worddoc, column1, column2):
	rows = max(len(column1), len(column2))
	table = createTable(worddoc, rows, 4)
	columns = map(None, column1, column2)
	row = 0
	for c1, c2 in columns:
		if c1 == None:
			c1 = (u'',)
		if c2 == None:
			c2 = (None,)
		if not (isinstance(c1, tuple) and isinstance(c2, tuple)):
			raise Exception("Error -- input is not tuple")
		cells = table.rows[row].cells
		row += 1
		addEntry(cells, 0, *c1)
		addEntry(cells, 2, *c2)

def setHeader(worddoc, data):
	p = worddoc.add_paragraph()
	r = p.add_run(data['text'])
	r.rtl = True
		
def createDoc():
	return Document("emptySched.docx")

def saveDoc(worddoc, monthName, year):
	worddoc.save(os.getcwd() + '\\' + monthName + repr(year) + '.docx')
