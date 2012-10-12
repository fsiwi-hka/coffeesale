#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from messageUi import Ui_MessageWindow

class MessageWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.ui=Ui_MessageWindow()
        self.ui.setupUi(self)
        
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.displayUpdate)
        self.timer.start(100)

        self.timeout = 5
        self.start = time.time()
        self.setModal(True)
        self.ui.message.setText("")

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.start = time.time()

    def resizeEvent(self, event):
        circleSize = 70
        offset = circleSize / 2

        mask = QtGui.QRegion(0, offset, self.width(), self.height()-offset*2, QtGui.QRegion.Rectangle)
        mask = mask.unite(QtGui.QRegion(offset, 0, self.width()-offset*2, self.height(), QtGui.QRegion.Rectangle))

        mask = mask.unite(QtGui.QRegion(0, 0, circleSize, circleSize, QtGui.QRegion.Ellipse))
        mask = mask.unite(QtGui.QRegion(self.width()-circleSize, 0, circleSize, circleSize, QtGui.QRegion.Ellipse))
        mask = mask.unite(QtGui.QRegion(0, self.height()-circleSize, circleSize, circleSize, QtGui.QRegion.Ellipse))
        mask = mask.unite(QtGui.QRegion(self.width()-circleSize, self.height()-circleSize, circleSize, circleSize, QtGui.QRegion.Ellipse))

        self.setMask(mask)
        return

    def show(self, message, timeout):
        QtGui.QDialog.show(self)
        #self.setWindowState(QtCore.Qt.WindowMaximized)
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

    def keyPressEvent(self, event):            
        #if event.key() == QtCore.Qt.Key_Escape:
        #self.close()
        return
