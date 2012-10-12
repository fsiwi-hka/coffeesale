#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os, random
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from screensaverUi import Ui_Screensaver

class ScreensaverWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.ui=Ui_Screensaver()
        self.ui.setupUi(self)
        
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.displayUpdate)
        self.timer.start(1000)


        self.start = time.time()
        self.timeout = 3

        self.setModal(True)

        self.ui.frame.setFrameShadow(QtGui.QFrame.Plain)
        return

    def show(self):
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setModal(True)
        self.start = time.time()
        self.shuffle()
        QtGui.QDialog.show(self)

        # EVIL HACK FOR XMONAD/X11/XORG
        desk = QtGui.QDesktopWidget()
        r = desk.screenGeometry()
        offset = 4
        self.setGeometry(r.left()-offset, r.top()-offset, r.width()+offset*2, r.height()+offset*2)

    def displayUpdate(self):
        t = time.time()


        if self.start + self.timeout < t:
            self.start = time.time()
            self.shuffle()

    def shuffle(self):
        offset = 25
        self.ui.frame.setGeometry(random.randint(0-offset, self.width() - self.ui.frame.width()+offset), random.randint(0-offset, self.height() - self.ui.frame.height()+offset), self.ui.frame.width(), self.ui.frame.height()) 

    def mousePressEvent(self, event):
        #button = event.button()
        self.close()

    def keyPressEvent(self, event):            
        #if event.key() == QtCore.Qt.Key_Escape:
        #self.close()
        return
