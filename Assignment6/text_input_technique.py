#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys
from PyQt5.QtWidgets import QCompleter, QLineEdit, QApplication
from PyQt5.QtCore import QStringListModel, Qt
from PyQt5 import QtGui, QtCore, QtWidgets
from text_entry_speed_test import TextInput


# Workload Distribution:
# The basics of the TextInput class were implemented together. The reading of the test configuration and the change of
# the input and the logging were implemented by Daniel Schmaderer.  The classes Completer and TextEdit in
# text_input_technique.py were basicly used from the source:
# https://stackoverflow.com/questions/35628257/pyqt-auto-completer-with-qlineedit-multiple-times
# and finished by Andreas Pfaffelhuber.
# The extended TextInputComparison for 6.3 was implemented by both members together.

# Implemented by Andreas Pfaffelhuber nearly exactly after
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


# Implemented by Andreas Pfaffelhuber nearly exactly after
# https://stackoverflow.com/questions/35628257/pyqt-auto-completer-with-qlineedit-multiple-times
class TextEdit(QtWidgets.QLineEdit):

    def get_data(self, model):
        model.setStringList(["Joe", "went", "to", "the", "store", "Sarah", "and", "Jessie", "are", "going",
                             "swimming", "frog", "jumped", "landed", "in", "pond", "Can", "I", "have", "some",
                             "juice", "drink", "pizza", "smells", "delicious", "there", "is", "a", "fly",
                             "car", "with", "us", "look", "on", "top", "of", "refrigerator", "for", "key",
                             "am", "out", "paper", "printer", "will", "you", "help", "me", "math" "homework",
                             "music", "too", "loud", "my", "ears"])

    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        model = QStringListModel()
        self._completer = Completer(self)
        self.setCompleter(self._completer)
        self._completer.setModel(model)
        self.get_data(model)


# Implemented by both members
# Extends the basic TextInput and overwrites some methods to allow for a change between autocompletion on and off
class TextInputComparison(TextInput):
    def __init__(self, user_id, sentences, sentences_number, trail_name):
        super(TextInput, self).__init__()
        self.timer = QtCore.QTime()
        self.timerSentence = QtCore.QTime()
        self.timerLastKey = QtCore.QTime()
        self.user_id = user_id
        self.sentences = sentences
        self.sentence_number = sentences_number
        self.sum_sentence_time_elapsed = 0
        self.trail_name = trail_name
        self.setHtml(self.sentences[0])
        self.sentence_counter = 0
        self.initUI()
        print("event; timestamp (ISO); user_id; sentence_number; time (ms); trail_name")

    # Initialize the QlineEdit and the TextEdit with same position, connect and show only the used one
    def textInputUI(self):
        self.text_input_autocomplete = TextEdit(self)
        self.text_input_autocomplete.setFixedWidth(300)
        self.text_input_autocomplete.move(5, 60)
        self.text_input_autocomplete.setPlaceholderText("Enter the sentences here")

        self.text_input = QtWidgets.QLineEdit(self)
        self.text_input.setFixedWidth(300)
        self.text_input.move(5, 60)
        self.text_input.setPlaceholderText("Enter the sentences here")

        if self.trail_name[self.sentence_counter] == "IT":
            self.text_input_autocomplete.textChanged.connect(self.input_change)
            self.text_input_autocomplete.editingFinished.connect(self.sentence_finished)
            self.text_input_autocomplete.setFocus()
            self.text_input.hide()
        else:
            self.text_input.textChanged.connect(self.input_change)
            self.text_input.editingFinished.connect(self.sentence_finished)
            self.text_input.setFocus()
            self.text_input_autocomplete.hide()

    # Changes the sentences and clears the Line and Text Edit when a user finished a sentence
    # Hides the currently shown edit and shows the other
    # Disconnects signals from the hidden edit and connects with the showed one
    def sentence_finished(self):
        sentence_time_elapsed = self.timerSentence.elapsed()
        self.sum_sentence_time_elapsed += self.timerSentence.elapsed()
        self.logging("sentence", sentence_time_elapsed)
        self.sentence_counter += 1
        if self.sentence_counter < len(self.sentences):
            self.setHtml(self.sentences[self.sentence_counter])
            self.text_input.setText("")
            self.text_input_autocomplete.setText("")
            if self.trail_name[self.sentence_counter] == "IT":
                self.text_input.textChanged.disconnect()
                self.text_input.editingFinished.disconnect()
                self.text_input_autocomplete.textChanged.connect(self.input_change)
                self.text_input_autocomplete.editingFinished.connect(self.sentence_finished)
                self.text_input_autocomplete.setFocus()
                self.text_input.hide()
                self.text_input_autocomplete.show()
            else:
                self.text_input_autocomplete.textChanged.disconnect()
                self.text_input_autocomplete.editingFinished.disconnect()
                self.text_input.textChanged.connect(self.input_change)
                self.text_input.editingFinished.connect(self.sentence_finished)
                self.text_input.setFocus()
                self.text_input_autocomplete.hide()
                self.text_input.show()
        else:
            self.logging_test_finished("test", self.sum_sentence_time_elapsed)
            sys.exit(1)


# Implemented by Daniel Schmaderer
# Main loop to show the application and read the input files
def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        filepath = sys.argv[1]
        with open(filepath) as f:
            d = json.load(f)
        text_input = TextInputComparison(d['userID'], d['sentences'], d['sentenceNumber'], d['trailName'])
        sys.exit(app.exec_())
    except Exception:
        print("An error occured while starting the programm. Please specify an input file with the correct format.")


if __name__ == '__main__':
    main()
