#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore, QtWidgets

# Workload Distribution:
# The basics of the TextInput class were implemented together. The reading of the test configuration and the change of
# the input and the logging were implemented by Daniel Schmaderer.  The classes Completer and TextEdit were basicly
# used from the source: https://stackoverflow.com/questions/35628257/pyqt-auto-completer-with-qlineedit-multiple-times
# and finished by Andreas Pfaffelhuber.

class TextInput(QtWidgets.QTextEdit):

    def __init__(self, example_text):
        super(TextInput, self).__init__()
        self.timer = QtCore.QTime()
        self.timerSentence = QtCore.QTime()
        self.user_id = "1"
        self.sentences = ['First Sentence', 'Second Sentence', 'Third Sentence']
        self.sentence_number = ['1', '2', '3']
        self.trail_name = ['IT', 'NI', 'IT' ]
        self.setHtml(self.sentences[0])
        self.sentence_counter = 0
        self.initUI()
        self.text_input.textChanged.connect(self.input_change)
        self.text_input.editingFinished.connect(self.sentence_finished)
        print("event; timestamp (ISO); user_id; sentence_number; time (ms); trail_name")

    def logging(self, event, time):
        print("%s; %s; %s; %s; %d; %s" % (event,
                                          self.timestamp(),
                                          self.user_id,
                                          self.sentence_number[self.sentence_counter],
                                          time,
                                          self.trail_name[self.sentence_counter]))

    # Loggs the input changes for the QLineEdit and starts the timers
    def input_change(self, text):
        if len(text) <= 1:
            self.timer.start()
            self.timerSentence.start()
        if text[-1:] == ' ':
            word_time_elapsed = self.timer.elapsed()
            self.logging("word", word_time_elapsed)
            self.timer.start()
        if text[-1:] != ' ':
            self.logging("key", 0)

    # Changes the sentences and clears the QlineEdit when a user finished a sentence
    def sentence_finished(self):
        sentence_time_elapsed = self.timerSentence.elapsed()
        self.logging("sentence", sentence_time_elapsed)
        self.sentence_counter += 1
        if self.sentence_counter < len(self.sentences):
            self.setHtml(self.sentences[self.sentence_counter])
            self.text_input.setText("")
            self.text_input.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.text_input.setFocus()
        else:
            sys.stderr.write("Test finished: There are no sentences left.")
            sys.exit(1)

    # Creates a timestamp in the ISO-format
    def timestamp(self):
        return QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)

    # Sets up the basic UI
    def initUI(self):
        self.setGeometry(0, 0, 500, 500)
        self.setWindowTitle('Text Entry Speed Test')
        self.textInputUI()
        self.show()

    # Initialize the QlineEdit and its position
    def textInputUI(self):
        self.text_input = QtWidgets.QLineEdit(self)
        self.text_input.setFixedWidth(300)
        self.text_input.move(5, 60)
        self.text_input.setPlaceholderText("Enter the sentences here")
        self.text_input.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.text_input.setFocus()


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        #filepath = sys.argv[1]
        #with open(filepath) as f:
        #    d = json.load(f)
        #text_input = TextInput(d['userID'], d['sentences'], d['sentenceNumber'], d['trailName])
        text_input = TextInput("An 1234 Tagen kamen 1342 Personen.")
        sys.exit(app.exec_())
    except Exception:
        print("An error occured while starting the programm. Please specify an input file with the correct format.")

if __name__ == '__main__':
    main()
