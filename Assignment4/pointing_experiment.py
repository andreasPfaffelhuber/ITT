import sys
import random
import math
from PyQt5 import QtGui, QtWidgets, QtCore


USERID = 1
SIZES = [30, 30, 30, 40, 10, 10, 10, 10]
DISTANCES = [100, 100, 100, 100, 300, 300, 50, 50]
POINTING_TECHNIQUE = [True, False, True, True, True, True, True, False]


class Circle(object):
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def get_position(self):
        return (self.x, self.y)

    def get_radius(self):
        return self.radius

    def intersects_circle(self, circle):
        squared_distance = (self.x - circle.x) * (self.x - circle.x) + (self.y - circle.y) * (self.y - circle.y)
        squared_radius = (self.radius + circle.radius) * (self.radius + circle.radius)
        if squared_radius < squared_distance:
            return False
        else:
            return True

    def within_circle(self, x, y):
        if (x - self.x) * (x - self.x) + (y - self.y) * (y - self.y) <= (self.radius * self.radius):
            return True
        else:
            return False


class FittsLawModel(object):
    def __init__(self, user_id, sizes, distances):
        self.timer = QtCore.QTime()
        self.user_id = user_id
        self.sizes = sizes
        self.distances = distances
        self.current_trial = -1
        print("timestamp (ISO); user_id; trial; target_distance; target_size; movement_time (ms);"
              " start_pos_x; start_pos_y; end_pos_x; end_pos_y; click_offset_x; click_offset_y; was_error")

    def get_current_trial(self):
        return self.current_trial

    def get_max_trials(self):
        return len(self.sizes)

    def get_current_trial_parameters(self):
        return (self.sizes[self.current_trial], self.distances[self.current_trial])

    def start_next_trial(self):
        if self.current_trial < len(self.sizes)-1:
            self.current_trial += 1
            self.timer.start()
        else:
            sys.stderr.write("There are no targets left.")
            sys.exit(1)

    def log_mousepress(self, start_pos, end_pos, click_offset, error):
        size, distance = self.get_current_trial_parameters()
        time_elapsed = self.timer.elapsed()
        print("%s; %s; %d; %d; %d; %d; %d; %d; %d; %d; %d; %d; %s" % (self.timestamp(), self.user_id,
                                                                      self.current_trial, distance, size, time_elapsed,
                                                                      start_pos[0], start_pos[1], end_pos[0],
                                                                      end_pos[1], click_offset[0],
                                                                      click_offset[1], error))

    def timestamp(self):
        return QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)


class FittsLawTest(QtWidgets.QWidget):
    def __init__(self, model):
        super(FittsLawTest, self).__init__()
        self.model = model
        self.screen_height = 400
        self.screen_width = 800
        self.start_pos = (self.screen_width/2, self.screen_height/2)
        self.initUI()
        self.target = None
        self.other_circles = None


    def initUI(self):
        self.text = "Press the left mouse button to start the experiment"
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        self.setWindowTitle('Fitts Law Test')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
        self.setMouseTracking(True)
        self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and self.model.get_current_trial() > -1:
            clicked_correct_target = self.target.within_circle(ev.x(), ev.y())
            current_position = (ev.x(), ev.y())
            click_offset = (self.target.get_position()[0] - current_position[0],
                            self.target.get_position()[1] - current_position[1])
            self.model.log_mousepress(self.start_pos, current_position, click_offset, not clicked_correct_target)
            if clicked_correct_target:
                self.endedTrial(ev)
        elif ev.button() == QtCore.Qt.LeftButton and self.model.get_current_trial() == -1:
                self.endedTrial(ev)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.model.get_current_trial() > -1:
            self.drawCircles(event, qp)
        else:
            self.displayInstructions(event, qp)
        qp.end()

    def endedTrial(self, event):
        self.model.start_next_trial()
        self.start_pos = (event.x(), event.y())
        self.setCircles(event)
        self.update()

    def displayInstructions(self, event, qp):
        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setFont(QtGui.QFont('Decorative', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    def target_pos(self, distance, size):
        found_new_target_pos = False
        while not found_new_target_pos:
            random_angle = random.randint(1, 359)
            rad_random_angle = math.radians(random_angle)

            x_change = distance*math.cos(rad_random_angle)
            y_change = distance*math.sin(rad_random_angle)

            x = self.start_pos[0] + x_change
            y = self.start_pos[1] + y_change

            if x > 0 + size and x < self.screen_width - size and y > 0 + size and y < self.screen_height - size:
                found_new_target_pos = True
        return (x, y)


    def setCircles(self, event):
        size, distance = self.model.get_current_trial_parameters()
        self.setTarget(event, distance, size)
        self.setOtherCircles(event, distance, size)

    def setTarget(self, event, distance, size):
        x, y = self.target_pos(distance, size)
        self.target = Circle(x, y, size)

    def setOtherCircles(self, event, disance, size):
        self.other_circles = []
        for i in range(0, 10):
            x = random.randrange(0 + int(size/2+1), self.screen_width - int(size/2+1), 1)
            y = random.randrange(0 + int(size/2+1), self.screen_height - int(size/2+1), 1)
            circle = Circle(x, y, size)
            intersectsOtherCircles = False
            for otherCircle in self.other_circles:
                if circle.intersects_circle(otherCircle):
                    intersectsOtherCircles = True
            if not circle.intersects_circle(self.target) and not intersectsOtherCircles:
                self.other_circles.append(circle)

    def drawCircles(self, event, qp):
        self.drawTarget(event, qp)
        self.drawOtherCircles(event, qp)

    def drawTarget(self, event, qp):
        x, y = self.target.get_position()
        size = self.target.get_radius()
        qp.setBrush(QtGui.QColor(200, 34, 20))
        qp.drawEllipse(x-size/2, y-size/2, size, size)

    def drawOtherCircles(self, event, qp):
        for circle in self.other_circles:
            x, y = circle.get_position()
            size = circle.get_radius()
            qp.setBrush(QtGui.QColor(1, 4, 2))
            qp.drawEllipse(x-size/2, y-size/2, size, size)


def main():
    app = QtWidgets.QApplication(sys.argv)
    model = FittsLawModel(1, SIZES, DISTANCES)
    fitts_law_test = FittsLawTest(model)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
