#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5 import QtGui, QtWidgets, QtCore
import datetime
import random
import csv
import time

class SpaceRecorder(QtWidgets.QWidget):
    """ Counts how often the 'space' key is pressed and displays the count.

    Every time the 'space' key is pressed, a visual indicator is toggled, too.
    """

    def __init__(self, participant, trials, time_between_signals):
        super().__init__()
        self.participant = participant
        self.trials = trials.split(", ")
        self.time_between_signals = time_between_signals
        self.starttime = None
        self.trialCount = 0
        self.is_blue_or_even = bool(random.getrandbits(1))
        self.is_between_signals = False



        self.logfile = open ("Participant" + self.participant + ".csv",'a')
        self.out = csv.DictWriter(self.logfile, ["participantID", "stimulus", "complexity",
                                                 "distraction", "pressedKey", "correctKey",
                                                 "reactionTime", "timestamp"])
        self.out.writeheader()
        self.initUI()

    def initUI(self):
        # set the text property of the widget we are inheriting
        self.text = "Press Space to start"
        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle('Reaction Time')
        # widget should accept focus by click and tab key
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.show()

    def keyPressEvent(self, ev):
        if ev.text() == "g" or ev.text() == "h":
            self.log()
            self.trialCount += 1
            self.is_blue_or_even = bool(random.getrandbits(1))
            if self.is_blue_or_even == True:
                self.text = str(random.randrange(2, 50, 2))
                self.color = "#00008B"
            else:
                self.text = str(random.randrange(1, 49, 2))
                self.color = "#B80000"
            self.is_between_signals = True
            self.update()
            time.sleep(1)
            #self.is_between_signals = False
            #self.starttime = datetime.datetime.now()
            #self.update()
        if ev.key() == QtCore.Qt.Key_Space:
            if self.is_blue_or_even == True:
                self.text = str(random.randrange(2, 50, 2))
                self.color = "#00008B"
            else:
                self.text = str(random.randrange(1, 49, 2))
                self.color = "#B80000"
            self.update()


    def paintEvent(self, event):

        qp = QtGui.QPainter()
        qp.begin(self)
        print(self.is_between_signals)
        if self.is_between_signals:
            print("ja")
            qp.setPen(QtGui.QColor(0, 0, 0))
            qp.setFont(QtGui.QFont('Decorative', 32))
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, "test")
        elif self.trials[self.trialCount] == "AD":
            self.drawText(event, qp)
        elif self.trials[self.trialCount] == "AN":
            self.drawText(event, qp)
        elif self.trials[self.trialCount] == "PD":
            self.drawRect(event, qp)
        elif self.trials[self.trialCount] == "PN":
            self.drawRect(event, qp)

        # self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setFont(QtGui.QFont('Decorative', 32))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)


    def drawRect(self, event, qp):
        rect = QtCore.QRect(210, 210, 80, 80)
        qp.setBrush(QtGui.QColor(self.color))
        qp.drawRoundedRect(rect, 10.0, 10.0)

    def log(self):
        pass



def main():
    app = QtWidgets.QApplication(sys.argv)
    # variable is never used, class automatically registers itself for Qt main loop:
    space = SpaceRecorder("1","AD, AN, PN, AD",1000)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
