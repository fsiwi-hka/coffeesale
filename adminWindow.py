#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from adminUi import Ui_AdminWindow

# Admin Item Window
from adminItemWindow import *

# Admin Statistics Window
from adminStatsWindow import *

class AdminWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window)
        self.ui=Ui_AdminWindow()
        self.ui.setupUi(self)
        self.setModal(True)
        self.adminItemWindow = AdminItemWindow(self)
        self.adminStatsWindow = AdminStatsWindow(self)
        self.ui.pushBack.clicked.connect(self.pushBack)
        self.ui.pushAdmin.clicked.connect(self.pushAdmin)
        self.ui.pushStats.clicked.connect(self.pushStats)

    def show(self):
        QtGui.QDialog.show(self)
        self.setWindowState(QtCore.Qt.Fullscreen)

    def close(self):
        self.adminItemWindow.close()
        self.adminStatsWindow.close()
        QtGui.QDialog.close(self)

    def pushBack(self):
        self.reject()

    def pushAdmin(self):
        self.adminItemWindow.exec_()
        self.raise_()
        self.activateWindow()

    def pushStats(self):
        # Workaround for Qt bug in AdminStatsWindow - QFormLayouts can not be reset properly
        self.adminStatsWindow.close()
        self.adminStatsWindow = AdminStatsWindow(self)
        self.adminStatsWindow.exec_()
        self.raise_()
        self.activateWindow()
