#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from messageUi import Ui_MessageWindow

class MessageWindow(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.ui=Ui_MessageWindow()
        self.ui.setupUi(self)
        
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.displayUpdate)
        self.timer.start(100)

        self.timeout = 5
        self.start = time.time()

        self.ui.message.setText("")

        self.start = time.time()

    def show(self, message, timeout):
        QtGui.QDialog.show(self)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.timeout = timeout
        self.start = time.time()
        self.ui.message.setText(message)

    def displayUpdate(self):
        t = time.time()

        if self.start + self.timeout < t:
            self.close()

    def mousePressEvent(self, event):
        #button = event.button()
        self.close()

    def keyPressEvent(self, e):            
        #if e.key() == QtCore.Qt.Key_Escape:
        self.close()
