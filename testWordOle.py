#!/usr/bin/python
# -*- coding: UTF-8 -*-
import win32com.client
 
def createTable(worddoc, rows, cols):
	loc = worddoc.Range()
	para = loc.Paragraphs.Add()
	loc.Collapse(0)
	table = loc.Tables.Add(loc, rows, cols)
	table.TableDirection = 0 # set table to RTL
	cell = table.Cell(1,1)
	
	return (loc, para, table, cell)

def addEntry(cell, name, time=None):
	if time:
		cell.Range.InsertAfter(name)
		cell = cell.Next
		cell.Range.InsertAfter(time)
		cell = cell.Next
	else:
		cell.Range.InsertAfter(name)
		cell.Merge(cell.Next)
		cell = cell.Next
	return cell
	
wordapp = win32com.client.gencache.EnsureDispatch("Word.Application")
wordapp.Visible = True # Word Application should be visible
worddoc = wordapp.Documents.Add() # Create new Document Object
worddoc.PageSetup.Orientation = 0 # Make some Setup to the Document:
worddoc.PageSetup.LeftMargin = 20
worddoc.PageSetup.TopMargin = 20
worddoc.PageSetup.BottomMargin = 20
worddoc.PageSetup.RightMargin = 20
worddoc.Content.Font.Size = 14
worddoc.Content.Paragraphs.TabStops.Add (100)
worddoc.Content.Text = u"בדיקת עברית (ועוד איך)"

(loc, para, table, cell) = createTable(worddoc, 4, 4)
#para.Range.Text = 'Some text'
for a in range(1,5):
	for b in range(1,5):
		table.Cell(a, b).Range.InsertAfter('a: %d, b: %d' % (a, b))
worddoc.Content.MoveEnd

worddoc.Range().Paragraphs.Add().Range.Text = "Testing 123"

(loc, para, table, cell) = createTable(worddoc, 4, 4)
#para.Range.Text = 'Some text'
for a in range(1,5):
	for b in range(1,5):
		cell.Range.InsertAfter('a: %d, b: %d' % (a, b))
		cell = cell.Next
worddoc.Content.MoveEnd

(loc, para, table, cell) = createTable(worddoc, 4, 4)
#para.Range.Text = 'Some text'
for a in range(1,5):
	for b in range(1,3):
		cell = addEntry(cell, "1", u"2")
worddoc.Content.MoveEnd

wordapp.ActiveDocument.SaveAs('test.docx')
#worddoc.Close() # Close the Word Document (a save-Dialog pops up)
#wordapp.Quit() # Close the Word Application