#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import time
import re

class TextInput(QtWidgets.QTextEdit):

    def __init__(self, example_text):
        super(TextInput, self).__init__()
        self.timer = QtCore.QTime()
        self.timerSentence = QtCore.QTime()
        self.setHtml(example_text)
        self.initUI()
        self.text_input.textChanged.connect(self.input_change)
        self.text_input.editingFinished.connect(self.sentence_finished)

    def input_change(self, text):
        if len(text) <= 1:
            self.timer.start()
            self.timerSentence.start()
        if text[-1:] == ' ':
            word_time_elapsed = self.timer.elapsed()
            print("Word input in ms: " + str(word_time_elapsed))
            self.timer.start()

    def sentence_finished(self):
        sentence_time_elapsed = self.timerSentence.elapsed()
        print("Sentence input in ms: " + str(sentence_time_elapsed))

    def initUI(self):
        self.setGeometry(0, 0, 500, 500)
        self.setWindowTitle('Text Entry Speed Test')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.textInputUI()
        self.show()

    # New
    def textInputUI(self):
        self.text_input = QtWidgets.QLineEdit(self)
        self.text_input.setFixedWidth(300)
        self.text_input.move(5, 30)
        self.text_input.setPlaceholderText("Enter the sentences here")

    # New
    def keyPressEvent(self, ev):
        super(TextInput, self).keyPressEvent(ev)
        if ev.key() == QtCore.Qt.Key_Space:
            print("Space")
        if ev.key() == QtCore.Qt.Key_Enter:
            print("Enter")

def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        #filepath = sys.argv[1]
        #with open(filepath) as f:
        #    d = json.load(f)
        #model = FittsLawModel(d['userID'], d['size'], d['distance'], d['trial'])
        #fitts_law_test = FittsLawTest(model)
        text_input = TextInput("An 1234 Tagen kamen 1342 Personen.")
        sys.exit(app.exec_())
    except Exception:
        print("An error occured while starting the programm. Please specify an input file with the correct format.")

if __name__ == '__main__':
    main()
