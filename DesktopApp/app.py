import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

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

    def gotoHome(self):
        self.widgets.setCurrentIndex(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widgets = QtWidgets.QStackedWidget()

    homeScreen = HomeScreen(widgets)
    menuScreen = MenuScreen(widgets)

    widgets.addWidget(homeScreen)
    widgets.addWidget(menuScreen)

    widgets.setFixedSize(800, 600)
    widgets.setWindowTitle('DrishtiCon')

    widgets.show()

    try:
        sys.exit(app.exec_())
    except:
        print('Exiting')
