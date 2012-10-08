#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from tosUi import Ui_TosWindow

class TosWindow(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.ui=Ui_TosWindow()
        self.ui.setupUi(self)
        self.ui.pushAccept.clicked.connect(self.pushAccept)
        self.ui.pushCancel.clicked.connect(self.pushCancel)

    def show(self):
        QtGui.QDialog.show(self)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setModal(True)

    def pushAccept(self):
        self.accept()

    def pushCancel(self):
        self.reject()
