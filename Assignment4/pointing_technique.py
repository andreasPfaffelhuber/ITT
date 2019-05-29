#!/usr/bin/python3
# -*- coding: utf-8 -*-import datetime

# How the pointing technique works:
# Whenever the user moves his mouse and fires a mouse move event, we save the coordinates of that event with the current
# timestamp. To extrapolate from this data and to find out which target he wants to click, we take the current position
# of his cursor, and the position that his cursor had at a specified time before (Here we decided to use 0.2 seconds).

# We then compute the angle between his past cursor position and his current one. Then we compute all the angles between
# his current mouse position and every possibly available target. We then choose the target which's angle with the
# current position is the most similar to his past cursor position and his current one, assuming that peole would move
# linear and directly to their target.


import sys
import json
import math
import datetime
from PyQt5 import QtGui, QtWidgets, QtCore
from pointing_experiment import FittsLawTest, FittsLawModel


# Workload Distribution:
# As mentioned in pointing_experiment.py, the classes of the PointingTechniqueFittsLawModel and
# PointingTechniqueFittsLawTest were implemented by Andreas Pfaffelhuber.
# The general pointing technique was implemented together again.

# https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value
def closest(list, Number):
    aux = []
    for valor in list:
        aux.append(abs(Number-valor))
    return aux.index(min(aux))


# Extends the classic FittsLawModel to also incorporate pointing techniques
# Implemented by Andreas Pfaffelhuber
class PointingTechniqueFittsLawModel(FittsLawModel):
        def __init__(self, user_id, sizes, distances, pointing_techniques, trials):
            self.timer = QtCore.QTime()
            self.user_id = user_id
            self.sizes = sizes
            self.distances = distances
            self.pointing_techniques = pointing_techniques
            self.current_trial = -1
            self.trials = trials
            self.errors = 0
            print("timestamp (ISO); user_id; trial; target_distance; target_size; movement_time (ms);"
                  " start_pos_x; start_pos_y; end_pos_x; end_pos_y; click_offset_x; click_offset_y; errors; "
                  "pointing_technique; trial_name")

        # Logging-function, prints logs to stdout in csv-format
        def log_mousepress(self, start_pos, end_pos, click_offset):
            size, distance = self.get_current_trial_parameters()
            technique = self.get_current_trial_technique()
            time_elapsed = self.timer.elapsed()
            trial = self.trials[self.current_trial]
            print("%s; %s; %d; %d; %d; %d; %d; %d; %d; %d; %d; %d; %d; %s; %s" % (self.timestamp(), self.user_id,
                                                                                  self.current_trial, distance, size,
                                                                                  time_elapsed, start_pos[0],
                                                                                  start_pos[1], end_pos[0],
                                                                                  end_pos[1], click_offset[0],
                                                                                  click_offset[1], self.errors,
                                                                                  technique, trial))

        def get_current_trial_technique(self):
            return self.pointing_techniques[self.current_trial]


# Extends the classic FittsLawTest to incorporate the pointer extrapolation and displays the highlighted target in a
# different color. Tracks clicks as if they were on the highlighted target.
# Implemented by Andreas Pfaffelhuber
class PointingTechniqueFittsLawTest(FittsLawTest):
    def __init__(self, model):
        super().__init__(model)
        self.pointer_extrapolation = None
        self.highlighted_circle = None

    # Closes current trial if the user hits the goal, logs all clicks wether they hit it or not, logs highlighted target
    # position
    def mousePressEvent(self, ev):
        if self.highlighted_circle:
            x, y = self.highlighted_circle.get_position()
        else:
            x, y = ev.x(), ev.y()
        if ev.button() == QtCore.Qt.LeftButton and self.model.get_current_trial() > -1:
            clicked_correct_target = self.target.within_circle(x, y)
            current_position = (x, y)
            click_offset = (self.target.get_position()[0] - current_position[0],
                            self.target.get_position()[1] - current_position[1])
            if clicked_correct_target:
                self.model.log_mousepress(self.start_pos, current_position, click_offset)
                self.endedTrial(ev)
            else:
                self.model.add_error()
        elif ev.button() == QtCore.Qt.LeftButton and self.model.get_current_trial() == -1:
            self.endedTrial(ev)

    # Uses every mouse move event to recalculate the cursor extrapolation and thus selects a displayed target
    def mouseMoveEvent(self, ev):
        if self.pointer_extrapolation:
            self.highlighted_circle = self.pointer_extrapolation.filter(ev)
            self.update()

    # Draws the displayed targets and the highlighted target
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.model.get_current_trial() > -1:
            self.drawCircles(event, qp)
        else:
            self.displayInstructions(event, qp)
        if self.highlighted_circle:
            x, y = self.highlighted_circle.get_position()
            size = self.highlighted_circle.get_radius()
            qp.setBrush(QtGui.QColor(51, 102, 0))
            qp.drawEllipse(x-size/2, y-size/2, size, size)
        qp.end()

    # Ends current trial and starts a new one, sets new circles for the current cursor position
    def endedTrial(self, ev):
            self.model.start_next_trial()
            self.start_pos = (ev.x(), ev.y())
            self.setCircles(ev)
            if self.model.get_current_trial_technique():
                self.pointer_extrapolation = PointerExtrapolation([self.target] + self.other_circles, 0.2)
                self.highlighted_circle = self.pointer_extrapolation.filter(ev)
            else:
                self.pointer_extrapolation = None
                self.highlighted_circle = None
            self.update()


# Uses movement extrapolation to predict where the user wants to go to as described above
# Implemented by Andreas Pfaffelhuber and Daniel Schmaderer
class PointerExtrapolation(object):
    def __init__(self, targets, time_between_extrapolation):
        self.targets = targets
        self.time_between_extrapolation = time_between_extrapolation
        self.pointer_coordinates = []

    # Saves all Movement Coordinates and uses those to extrapolate future targets, returns the most likely target
    def filter(self, event):
        pointer_coordinate = (event.x(), event.y(), datetime.datetime.now())
        # if len(self.pointer_coordinates) > 5000:
        #    self.pointer_coordinates.pop(0)
        self.pointer_coordinates.append(pointer_coordinate)

        # if the cursor is on a target than this is the selected target
        for target in self.targets:
            if target.within_circle(event.x(), event.y()):
                return target

        if len(self.pointer_coordinates) < 2:
            return None

        past_pointer_coordinate_index = None

        # Takes the first coordinates that go back farther than the specified time
        for i in range(len(self.pointer_coordinates) - 1, -1, -1):
            if (pointer_coordinate[2] - self.pointer_coordinates[i][2]).total_seconds() > \
                    self.time_between_extrapolation or i == 0:
                past_pointer_coordinate_index = i
                break

        if not past_pointer_coordinate_index:
            past_pointer_coordinate_index = len(self.pointer_coordinates)-2

        past_x = self.pointer_coordinates[past_pointer_coordinate_index][0]
        past_y = self.pointer_coordinates[past_pointer_coordinate_index][1]

        # Computes the angle between the chosen past point and the current position
        # https://stackoverflow.com/questions/42258637/how-to-know-the-angle-between-two-points
        extrapolated_moving_angle = math.atan2(past_y - event.y(), past_x - event.x())

        # Finds the target which has the closest angle to the computed extrapolation and returns
        # it as the most likely goal
        angles = []
        for target in self.targets:
            angles.append(math.atan2(event.y() - target.get_position()[1], event.x() - target.get_position()[0]))

        extrapolated_target = self.targets[closest(angles, extrapolated_moving_angle)]
        return extrapolated_target


# Reads test configuration from json file and starts the programm
# Implemented by Daniel Schmaderer
def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        filepath = sys.argv[1]
        with open(filepath) as f:
            d = json.load(f)
        model = PointingTechniqueFittsLawModel(d['userID'], d['size'],
                                               d['distance'], d['pointingTechnique'], d['trial'])
        fitts_law_test = PointingTechniqueFittsLawTest(model)
        sys.exit(app.exec_())
    except Exception:
        print("An error occured while starting the programm. Please specify an input file with the correct format.")


if __name__ == '__main__':
    main()
