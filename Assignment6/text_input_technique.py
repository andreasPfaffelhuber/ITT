#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtWidgets import QCompleter, QLineEdit, QApplication
from PyQt5.QtCore import QStringListModel, Qt
from PyQt5 import QtGui, QtCore, QtWidgets
from text_entry_speed_test import TextInput

# https://stackoverflow.com/questions/35628257/pyqt-auto-completer-with-qlineedit-multiple-times

class Completer(QtWidgets.QCompleter):

    def __init__(self, parent=None):
        super(Completer, self).__init__(parent)

        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.setWrapAround(False)

    # Add texts instead of replace
    def pathFromIndex(self, index):
        path = QtWidgets.QCompleter.pathFromIndex(self, index)

        lst = str(self.widget().text()).split(' ')

        if len(lst) > 1:
            path = '%s %s' % (' '.join(lst[:-1]), path)

        return path

    # Add operator to separate between texts
    def splitPath(self, path):
        path = str(path.split(' ')[-1]).lstrip(' ')
        return [path]


class TextEdit(QtWidgets.QLineEdit):

    def get_data(self, model):
        model.setStringList(["completion", "data", "goes", "here"])

    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)

        self.setPlaceholderText("example : ")
        #words = ["alpha", "omega", "omicron", "zeta"]
        model = QStringListModel()
        self._completer = Completer(self)
        self.setCompleter(self._completer)
        self._completer.setModel(model)
        self.get_data(model)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TextEdit()
    w.show()
    #edit = QLineEdit()
    #completer = QCompleter()
    #edit.setCompleter(completer)
    #model = QStringListModel()
    #completer.setModel(model)
    #get_data(model)
    #edit.show()
    sys.exit(app.exec_())
