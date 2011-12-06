#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from mainUi import Ui_MainWindow

# Code window
from codeWindow import *

# Interaction timeout in seconds
MAIN_INTERACTION_TIMEOUT = 5

# WTF PYTHON?!
EURO = QtGui.QApplication.translate("", "€", None, QtGui.QApplication.UnicodeUTF8)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        # Setup signals
        self.ui.pushCoffee.clicked.connect(self.pushCoffeeClicked)
        self.ui.pushClubMate.clicked.connect(self.pushMateClicked)
        self.ui.pushCharge.clicked.connect(self.pushChargeClicked)

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.displayUpdate)
        self.timer.start(100)

        # Code Window
        self.codeWindow = CodeWindow()
        self.codeWindow.setModal(True)

        # Business logic stuff
        self.lastInteraction = time.time()

    def displayUpdate(self):
        t = time.time()

        # Reset selection if no interaction is made after specified time
        if self.lastInteraction + MAIN_INTERACTION_TIMEOUT < t:
            self.lastInteraction = t
            self.ui.pushClubMate.setChecked(False)
            self.ui.pushCoffee.setChecked(False)

        if self.ui.pushCoffee.isChecked():
            self.ui.message.setText("Bitte Karte anlegen: Kaffee - 0,50" + EURO)
        elif self.ui.pushClubMate.isChecked():
            self.ui.message.setText("Bitte Karte anlegen: Club Mate - 1,50" + EURO)
        else:
            self.ui.message.setText("Bitte Karte anlegen ...")

    def pushMateClicked(self):
        self.lastInteraction = time.time()
        self.ui.pushClubMate.setChecked(True)
        self.ui.pushCoffee.setChecked(False)
        self.displayUpdate()
        
    def pushCoffeeClicked(self):
        self.lastInteraction = time.time()
        self.ui.pushClubMate.setChecked(False)
        self.ui.pushCoffee.setChecked(True)
        self.displayUpdate()

    def pushChargeClicked(self):
        self.lastInteraction = 0
        self.codeWindow.show()

