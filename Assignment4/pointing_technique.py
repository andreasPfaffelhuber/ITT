import datetime
import sys
import random
import math
from PyQt5 import QtGui, QtWidgets, QtCore
from pointing_experiment import FittsLawTest, FittsLawModel


USERID = 1
SIZES = [30, 30, 30, 40, 10, 10, 10, 10]
DISTANCES = [100, 100, 100, 100, 300, 300, 50, 50]
POINTING_TECHNIQUES = [True, False, True, True, True, True, True, False]


#https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value
def closest(list, Number):
    aux = []
    for valor in list:
        aux.append(abs(Number-valor))
    return aux.index(min(aux))


class PointingTechniqueFittsLawModel(FittsLawModel):
        def __init__(self, user_id, sizes, distances, pointing_techniques):
            self.timer = QtCore.QTime()
            self.user_id = user_id
            self.sizes = sizes
            self.distances = distances
            self.pointing_techniques = pointing_techniques
            self.current_trial = -1
            print("timestamp (ISO); user_id; trial; target_distance; target_size; movement_time (ms);"
                  " start_pos_x; start_pos_y; end_pos_x; end_pos_y; click_offset_x; click_offset_y; was_error; "
                  "pointing_technique")

        def log_mousepress(self, start_pos, end_pos, click_offset, error):
            size, distance = self.get_current_trial_parameters()
            technique = self.get_current_trial_technique()
            time_elapsed = self.timer.elapsed()
            print("%s; %s; %d; %d; %d; %d; %d; %d; %d; %d; %d; %d; %s; %s" % (self.timestamp(), self.user_id,
                                                                          self.current_trial, distance, size, time_elapsed,
                                                                          start_pos[0], start_pos[1], end_pos[0],
                                                                          end_pos[1], click_offset[0],
                                                                          click_offset[1], error, technique))

        def get_current_trial_technique(self):
            return self.pointing_techniques[self.current_trial]


class PointingTechniqueFittsLawTest(FittsLawTest):
    def __init__(self, model):
        super().__init__(model)
        self.pointer_extrapolation = None
        self.highlighted_circle = None


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
            self.model.log_mousepress(self.start_pos, current_position, click_offset, not clicked_correct_target)
            if clicked_correct_target:
                self.endedTrial(ev)
        elif ev.button() == QtCore.Qt.LeftButton and self.model.get_current_trial() == -1:
            self.endedTrial(ev)

    def mouseMoveEvent(self, ev):
        if self.pointer_extrapolation:
            self.highlighted_circle = self.pointer_extrapolation.filter(ev)
            self.update()

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
            qp.setBrush(QtGui.QColor(0, 0, 102))
            qp.drawEllipse(x-size/2, y-size/2, size, size)
        qp.end()

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


class PointerExtrapolation(object):
    def __init__(self, targets, time_between_extrapolation):
        self.targets = targets
        self.time_between_extrapolation = time_between_extrapolation
        self.pointer_coordinates = []

    def filter(self, event):
        pointer_coordinate = (event.x(), event.y(), datetime.datetime.now())
        #if len(self.pointer_coordinates) > 5000:
        #    self.pointer_coordinates.pop(0)
        self.pointer_coordinates.append(pointer_coordinate)


        for target in self.targets:
            if target.within_circle(event.x(), event.y()):
                return target

        if len(self.pointer_coordinates) < 2:
            return None

        past_pointer_coordinate_index = None

        for i in range( len(self.pointer_coordinates) - 1, -1, -1):
            if (pointer_coordinate[2]- self.pointer_coordinates[i][2]).total_seconds() > self.time_between_extrapolation\
                    or i == 0:
                past_pointer_coordinate_index = i
                break

        if not past_pointer_coordinate_index:
            past_pointer_coordinate_index = len(self.pointer_coordinates)-2

        past_x = self.pointer_coordinates[past_pointer_coordinate_index][0]
        past_y = self.pointer_coordinates[past_pointer_coordinate_index][1]


        #https://stackoverflow.com/questions/42258637/how-to-know-the-angle-between-two-points
        extrapolated_moving_angle =  math.atan2(past_y - event.y(), past_x - event.x())

        angles = []
        for target in self.targets:
            angles.append(math.atan2(event.y() - target.get_position()[1], event.x() - target.get_position()[0]))

        extrapolated_target = self.targets[closest(angles,extrapolated_moving_angle)]
        return extrapolated_target


def main():
    app = QtWidgets.QApplication(sys.argv)
    model = PointingTechniqueFittsLawModel(1, SIZES, DISTANCES, POINTING_TECHNIQUES)
    fitts_law_test = PointingTechniqueFittsLawTest(model)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()




