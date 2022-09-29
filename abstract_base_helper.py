import abc


class DocumentHelperInterface(metaclass=abc.ABCMeta):

    @staticmethod
    def add_entry(cell, name, time=None):
        raise NotImplementedError

    @staticmethod
    def create_table(worddoc, rows, cols):
        raise NotImplementedError

    @staticmethod
    def create_populate_table(worddoc, column1, column2):
        raise NotImplementedError

    @staticmethod
    def set_header(worddoc, data):
        raise NotImplementedError

    @staticmethod
    def create_doc():
        raise NotImplementedError

    @staticmethod
    def create_sheet():
        raise NotImplementedError

    @staticmethod
    def set_row(sheet, row, date, name, shlishit=True):
        raise NotImplementedError

    @staticmethod
    def save_doc(worddoc, month_name, year):
        raise NotImplementedError

    @staticmethod
    def save_sheet(sheet, year):
        raise NotImplementedError
