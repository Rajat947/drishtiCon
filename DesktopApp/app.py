import sys
import numpy as np
import cv2
import dlib

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

from PyQt5.uic import loadUi


class HomeScreen(QMainWindow):
    def __init__(self, widgets):
        super(HomeScreen, self).__init__()
        loadUi('home.ui', self)

        self.widgets = widgets

        self.btnStart.clicked.connect(self.gotoMainMenu)

    def gotoMainMenu(self):
        self.widgets.setCurrentIndex(widgets.currentIndex() + 1)


class MenuScreen(QMainWindow):
    def __init__(self, widgets):
        super(MenuScreen, self).__init__()
        loadUi('menu.ui', self)

        self.widgets = widgets

        self.btnHome.clicked.connect(self.gotoHome)
        self.btnAcuity.clicked.connect(self.startVisionAcuity)

    def gotoHome(self):
        self.widgets.setCurrentIndex(0)

    def startVisionAcuity(self):
        self.widgets.setCurrentIndex(widgets.currentIndex() + 1)


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    change_dist_signal = pyqtSignal(int)

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(
        './detector/shape_predictor_68_face_landmarks.dat')

    left = [36, 37, 38, 39, 40, 41]
    right = [42, 43, 44, 45, 46, 47]

    kernel = np.ones((9, 9), np.uint8)

    focal_length = 1076.92
    iris_diameter_cm = 1.17

    def shape_to_np(self, shape, dtype='int'):
        # initialize the list of (x, y)-coordinates
        coords = np.zeros((68, 2), dtype=dtype)
        # loop over the 68 facial landmarks and convert them
        # to a 2-tuple of (x, y)-coordinates
        for i in range(0, 68):
            coords[i] = (shape.part(i).x, shape.part(i).y)
        # return the list of (x, y)-coordinates
        return coords

    def eye_on_mask(self, shape, mask, side):
        points = [shape[i] for i in side]
        points = np.array(points, dtype=np.int32)
        mask = cv2.fillConvexPoly(mask, points, 255)
        return mask

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 260)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 180)
        while True:
            ret, img = cap.read()
            dist, ctr = 0, 0
            if ret:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                rects = self.detector(gray, 1)
                for rect in rects:
                    shape = self.predictor(gray, rect)
                    shape = self.shape_to_np(shape)
                    mask = np.zeros(img.shape[:2], dtype=np.uint8)
                    mask = self.eye_on_mask(shape, mask, self.left)
                    mask = self.eye_on_mask(shape, mask, self.right)
                    mask = cv2.dilate(mask, self.kernel, 5)
                    eyes = cv2.bitwise_and(img, img, mask=mask)
                    mask = (eyes == [0, 0, 0]).all(axis=2)
                    eyes[mask] = [255, 255, 255]
                    iris_diam_px = abs(shape[42][0] - shape[39][0])
                    iris_depth = (self.focal_length *
                                  self.iris_diameter_cm) / iris_diam_px
                    dist += iris_depth
                    ctr += 1

                if ctr == 0:
                    ctr = 1
                dist = dist / ctr
                self.change_pixmap_signal.emit(img)
                self.change_dist_signal.emit(int(dist))


class VisionAcuity(QMainWindow):
    userSittingImproperly = 20

    def __init__(self):
        super(VisionAcuity, self).__init__()
        loadUi('acuity_dist.ui', self)

        self.disply_width = 260
        self.display_height = 220

        # create the video capture thread
        self.video_thread = VideoThread()
        # connect its signal to the update_image slot
        self.video_thread.change_pixmap_signal.connect(self.updateImage)
        self.video_thread.change_dist_signal.connect(self.updateDistLabel)
        # start the thread
        self.video_thread.start()

    @pyqtSlot(int)
    def updateDistLabel(self, dist):
        self.dist_label.setText(f'{dist} cm')
        if dist >= 90 and dist <= 110:
            self.image_label.setStyleSheet('border: 3px solid lightgreen')
            self.userSittingImproperly = 0
        else:
            if self.userSittingImproperly > 5:
                self.image_label.setStyleSheet('border: 3px solid red')
            self.userSittingImproperly += 1

    @pyqtSlot(np.ndarray)
    def updateImage(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(
            rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(
            self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widgets = QtWidgets.QStackedWidget()

    homeScreen = HomeScreen(widgets)
    menuScreen = MenuScreen(widgets)
    visionAcuityDist = VisionAcuity()

    widgets.addWidget(homeScreen)
    widgets.addWidget(menuScreen)
    widgets.addWidget(visionAcuityDist)

    widgets.setFixedSize(800, 600)
    widgets.setWindowTitle('DrishtiCon')

    widgets.show()

    try:
        sys.exit(app.exec_())
    except:
        print('Exiting')
