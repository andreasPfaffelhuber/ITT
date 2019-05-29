import datetime
import sys
import random
import math
from PyQt5 import QtGui, QtWidgets, QtCore
#from pointing_experiment import Circle, FittsLawTest, FittsLawModel

#https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value
def closest(list, Number):
    aux = []
    for valor in list:
        aux.append(abs(Number-valor))
    return aux.index(min(aux))

class PointerExtrapolation(object):
    def __init__(self, targets, time_between_extrapolation):
        self.targets = targets
        self.time_between_extrapolation = time_between_extrapolation
        self.pointer_coordinates = []

    def updateTargets(self, targets):
        self.targets = targets

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
                print(past_pointer_coordinate_index)
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



