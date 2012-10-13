#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from adminUi import Ui_AdminWindow

class AdminWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window)

        self.ui=Ui_AdminWindow()
        self.ui.setupUi(self)

    def show(self):
        QtGui.QDialog.show(self)
        self.setWindowState(QtCore.Qt.Fullscreen)
        self.setModal(True)


