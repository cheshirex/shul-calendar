#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import win32com.client
import itertools

from abstract_base_helper import DocumentHelperInterface


class OleHelper(DocumentHelperInterface):
	@staticmethod
	def add_entry(cell, name, time=None):
		if name is None:
			# Special case -- merge this cell with the preceding and following cell
			cell.Merge(cell.Next)
			next_cell = cell.Next
			cell.Merge(cell.Previous)
			return next_cell
		if isinstance(name, str):
			name = {'text': name}
		if 'bold' in name and name['bold']:
			cell.Range.Font.BoldBi = True
		cell.Range.Text = name['text']
		cell.Range.Font.SizeBi = 14
		cell.Range.Font.Name = "Arial"
		if time:
			if isinstance(time, str):
				time = {'text': time}
			if 'bold' in time and time['bold']:
				cell.Range.Font.BoldBi = True
			cell = cell.Next
			cell.Range.Text = time['text']
			cell.Range.Font.SizeBi = 14
			cell.Range.Font.Name = "Arial"
		else:
			cell.Merge(cell.Next)
		cell = cell.Next
		return cell

	@staticmethod
	def create_table(worddoc, rows, cols):
		loc = worddoc.Range()
		loc.Collapse(0)
		table = loc.Tables.Add(loc, rows, cols)
		table.TableDirection = 0  # set table to RTL
		for column in table.Columns:
			if column.Index % 2 == 0:
				column.Width = 70
				if column.IsLast:
					column.Width = 100
			else:
				column.Width = 150

		return table

	# For now, hardcoded to four columns
	def create_populate_table(self, worddoc, column1, column2):
		rows = max(len(column1), len(column2))
		table = self.create_table(worddoc, rows, 4)
		columns = itertools.zip_longest(column1, column2, fillvalue=None)
		# columns = map(None, column1, column2)
		cell = table.Cell(1, 1)
		for c1, c2 in columns:
			if c1 is None:
				c1 = (u'',)
			if c2 is None:
				c2 = (None,)
			if not (isinstance(c1, tuple) and isinstance(c2, tuple)):
				raise Exception("Error -- input is not tuple")
			cell = self.add_entry(cell, *c1)
			cell = self.add_entry(cell, *c2)

	@staticmethod
	def set_header(worddoc, data):
		r = worddoc.Range().Paragraphs.Add().Range
		if 'size' not in data:
			size = 16
		else:
			size = data['size']
		r.Font.SizeBi = size
		r.Font.Name = "Arial"
		if 'bold' not in data or data['bold']:
			r.Font.BoldBi = True
		if 'italic' in data and data['italic']:
			r.Font.BoldBi = True
		r.Text = data['text']
		return r

	@staticmethod
	def create_doc():
		wordapp = win32com.client.gencache.EnsureDispatch("Word.Application")
		wordapp.Visible = True  # Word Application should be visible

		worddoc = wordapp.Documents.Open(os.getcwd() + "\\emptySched.docx", False, False, False)

		worddoc.Content.Font.Size = 14
		# worddoc.Content.Paragraphs.TabStops.Add (100)

		return worddoc

	@staticmethod
	def create_sheet():
		excelsheet = win32com.client.gencache.EnsureDispatch("Excel.Application")
		excelsheet.Visible = True  # Word Application should be visible

		excelsheet = excelsheet.Workbooks.Open(os.getcwd() + "\\emptyParshaSheet.xlsx", False, False)

		sheet = excelsheet.Worksheets("Sheet1")
		sheet.Activate()

		return sheet

	@staticmethod
	def set_row(sheet, row, date, name, shlishit=True):
		sheet.Range('A%d' % row).Value = date
		sheet.Range('B%d' % row).Value = name
		if not shlishit:
			sheet.Range('E%d' % row).Interior.Pattern = -4124  # 25% gray

	@staticmethod
	def save_doc(worddoc, month_name, year):
		worddoc.SaveAs(os.getcwd() + '\\' + month_name + repr(year) + '.docx')

	@staticmethod
	def save_sheet(sheet, year):
		sheet.SaveAs(os.getcwd() + '\\parshaSheet' + repr(year) + '.xlsx')
