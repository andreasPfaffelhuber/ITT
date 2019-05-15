#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5 import QtGui, QtWidgets, QtCore
import datetime
import random
import csv


ATTENTIVE_NO_DISTRACTION = "AN"
ATTENTIVE_DISTRACTION = "AD"
PRE_ATTENTIVE_NO_DISTRACTION = "PN"
PRE_ATTENTIVE_DISTRACTION = "PD"

COLOR_BLUE = "#00008B"
COLOR_RED = "#B80000"
COLOR_GREEN = "#008000"
COLOR_BLACK = "#000000"

class ReactionTimer(QtWidgets.QWidget):
    """
    Displays either even or odd numbers, or blue or red rectangles, with either dots as distraction
    in the background or without any distraction. Gives the user the chance to press one of two corresponding keys,
    and logs if the correct key was pressed.
    """

    def __init__(self, participant, trials, time_between_signals):
        super().__init__()
        # Initializes participants and trials, as well as the time spent waiting between signals
        self.participant = participant
        self.trials = trials.split(", ")
        self.time_between_signals = time_between_signals

        # Variables to adjust the programm flow
        self.is_between_signals = True
        self.trial_count = -1
        self.experiment_has_started = False
        self.experiment_has_ended = False
        self.choice_allowed = False
        self.displayed_stimulus ="Please press 'Space' to start."

        # Sets up up CSV-File for logging purposes
        self.logfile = open ("Participant" + self.participant + ".csv",'a')
        self.out = csv.DictWriter(self.logfile, ["ParticipantID", "Stimulus", "Complexity",
                                                 "Distraction", "PressedKey", "CorrectKey",
                                                 "ReactionTime", "Timestamp"])
        self.out.writeheader()
        self.initUI()

    # Displays the used window
    def initUI(self):
        self.setGeometry(300, 100, 600, 600)
        self.setWindowTitle('Reaction Time Test')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.show()

    # Called whenever a new trial starts, sets up variables and timer to wait out the time between signals
    def startNewTrial(self):
        self.is_between_signals = True
        self.trial_count += 1
        self.is_blue_or_even = random.choice([True, False])
        self.setDisplayedStimulus()
        self.update()
        self.timer = QtCore.QTimer(self)
        self.timer.singleShot(self.time_between_signals, self.displayTrial)

    # Displays the current trial after the time limit has been reached
    def displayTrial(self):
        self.is_between_signals = False
        self.choice_allowed = True
        self.trial_starttime = datetime.datetime.now()
        self.update()

    # Sets the displayed color or the displayed number for the current trial, which gets drawn later
    def setDisplayedStimulus(self):
        if self.trials[self.trial_count] == PRE_ATTENTIVE_DISTRACTION or \
        self.trials[self.trial_count] == PRE_ATTENTIVE_NO_DISTRACTION:
            if self.is_blue_or_even:
                self.displayed_stimulus = COLOR_BLUE
            else:
                self.displayed_stimulus = COLOR_RED
        else:
            if self.is_blue_or_even:
                self.displayed_stimulus = str(random.randrange(2, 50, 2))
            else:
                self.displayed_stimulus = str(random.randrange(1, 49, 2))

    # Ends the current trial, logs the acquired Data to the CSV and continues the programm flow afterwards
    def endTrial(self, event):
        self.logTrialToCSV(event)
        self.choice_allowed = False
        if self.trial_count < len(self.trials)-1:
            self.startNewTrial()
        elif self.trial_count == len(self.trials)-1:
            self.experiment_has_ended = True
            self.displayed_stimulus = "Vielen Dank für ihre Teilnahme"
            self.logfile.close()
            self.update()

    # Accepts space to start the entire experiment, and 'g' or 'h' when the user currently sees a trial's stimulus
    def keyPressEvent(self, ev):
        if ev.text() == "g" or ev.text() == "h":
            if self.experiment_has_started and not self.experiment_has_ended and self.choice_allowed:
                self.endTrial(ev)
        if ev.key() == QtCore.Qt.Key_Space:
            if not self.experiment_has_started and not self.experiment_has_ended:
                self.experiment_has_started = True
                self.startNewTrial()

    # Draws the currently displayed Stimulus, sets up a timer if there is a distraction in order to change
    # the dots in the background every x miliseconds
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.experiment_has_ended or not self.experiment_has_started:
            self.drawIntroOutroText(event, qp)
        elif not self.is_between_signals:
            if self.trials[self.trial_count] == ATTENTIVE_DISTRACTION:
                self.drawDistraction(event, qp)
                self.drawText(event, qp)
                self.updateTimer = QtCore.QTimer(self)
                self.updateTimer.singleShot(100, self.update)
            elif self.trials[self.trial_count] == ATTENTIVE_NO_DISTRACTION:
                self.drawText(event, qp)
            elif self.trials[self.trial_count] == PRE_ATTENTIVE_DISTRACTION:
                self.drawDistraction(event, qp)
                self.drawRect(event, qp)
                self.updateTimer = QtCore.QTimer(self)
                self.updateTimer.singleShot(100, self.update)
            elif self.trials[self.trial_count] == PRE_ATTENTIVE_NO_DISTRACTION:
                self.drawRect(event, qp)
        qp.end()

    # Draws the number for the current trial
    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setFont(QtGui.QFont('Decorative', 40))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.displayed_stimulus)

    # Draws the intro and outro for the experiment
    def drawIntroOutroText(self, event, qp):
        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setFont(QtGui.QFont('Decorative', 20))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.displayed_stimulus)

    # Draws the rectangle for the current trial
    def drawRect(self, event, qp):
        rect = QtCore.QRect(250, 250, 100, 100)
        qp.setBrush(QtGui.QColor(self.displayed_stimulus))
        qp.drawRoundedRect(rect, 10.0, 10.0)

    # Draws a lot of points in the background as a distraction
    def drawDistraction(self, event, qp):
        qp.setPen(QtGui.QColor(COLOR_GREEN))
        for i in range(8000):
            x = random.randint(1, 599)
            y = random.randint(1, 599)
            qp.drawPoint(x, y)
        qp.setPen(QtGui.QColor(COLOR_BLACK))


    def logTrialToCSV(self, event):
        # Sets Attentive/Pre-Attentive and Distraction/No Distraction based on the trial
        if self.trials[self.trial_count] == ATTENTIVE_DISTRACTION or \
        self.trials[self.trial_count] == ATTENTIVE_NO_DISTRACTION:
            complexity = "Attentive"
        else:
            complexity = "Pre-attentive"
        if self.trials[self.trial_count] == ATTENTIVE_DISTRACTION or \
        self.trials[self.trial_count] == PRE_ATTENTIVE_DISTRACTION:
            distraction = "Yes"
        else:
            distraction = "No"

        if self.is_blue_or_even:
            if event.text() == "g":
                correct_key = "Yes"
            else:
                correct_key = "No"
        else:
            if event.text() == "h":
                correct_key = "Yes"
            else:
                correct_key = "No"

        reaction_time = datetime.datetime.now() - self.trial_starttime

        entry = {"ParticipantID": self.participant, "Stimulus": self.displayed_stimulus,
                 "Complexity": complexity, "Distraction": distraction,
                 "PressedKey": event.key(), "CorrectKey": correct_key,
                 "ReactionTime": reaction_time, "Timestamp": datetime.datetime.now()}
        self.out.writerow(entry)



def main():
    # Reads given file from commandline parameter and extracts the given information
    filepath = sys.argv[1]
    participant = ""
    trials = ""
    time_between_signals_ms = 0
    f = open(filepath)
    contents = f.read()
    file_as_list = contents.splitlines()
    for line in file_as_list:
        line = line.split(": ")
        if line[0] == "PARTICIPANT":
            participant = line[1]
        if line[0] == "TRIALS":
            trials = line[1]
        if line[0] == "TIME_BETWEEN_SIGNALS_MS":
            time_between_signals_ms = int(line[1])
    app = QtWidgets.QApplication(sys.argv)
    react = ReactionTimer(participant,trials,time_between_signals_ms)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
