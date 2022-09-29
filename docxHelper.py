#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from docx import Document
from docx.enum.table import WD_TABLE_DIRECTION

from abstract_base_helper import DocumentHelperInterface


class DocxHelper(DocumentHelperInterface):
    @staticmethod
    def add_entry(cells, offset, name, time=None):
        if name is None:
            # Special case -- merge this cell with the preceding and following cell
            return
        if isinstance(name, str):
            name = {'text': name}
        if 'bold' in name and name['bold']:
            pass
        if time:
            if isinstance(time, str):
                time = {'text': time}
            cells[0 + offset].text = name['text']
            cells[0 + offset].paragraphs[0].runs[0].rtl = True
            cells[1 + offset].text = time['text']
            cells[1 + offset].paragraphs[0].runs[0].rtl = True
        else:
            cells[0 + offset].text = name['text']  # Need to figure out how to span multiple columns
            cells[0 + offset].paragraphs[0].runs[0].rtl = True

    @staticmethod
    def create_table(worddoc, rows, cols):
        table = worddoc.add_table(rows=rows, cols=cols)
        table.table_direction = WD_TABLE_DIRECTION.RTL
        return table

    # For now, hardcoded to four columns
    def create_populate_table(self, worddoc, column1, column2):
        rows = max(len(column1), len(column2))
        table = self.create_table(worddoc, rows, 4)
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
            self.add_entry(cells, 0, *c1)
            self.add_entry(cells, 2, *c2)

    @staticmethod
    def set_header(worddoc, data):
        p = worddoc.add_paragraph()
        r = p.add_run(data['text'])
        r.rtl = True

    @staticmethod
    def create_doc():
        return Document("emptySched.docx")

    @staticmethod
    def save_doc(worddoc, month_name, year):
        worddoc.save(f'{os.getcwd()}{os.sep}{month_name}{year}.docx')

    @staticmethod
    def create_sheet():
        pass

    @staticmethod
    def set_row(sheet, row, date, name, shlishit=True):
        pass

    @staticmethod
    def save_sheet(sheet, year):
        pass
