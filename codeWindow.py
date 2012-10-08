#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from codeUi import Ui_CodeWindow

# Interaction timeout in seconds
CODE_INTERACTION_TIMEOUT = 10

# WTF PYTHON?!
EURO = QtGui.QApplication.translate("", "€", None, QtGui.QApplication.UnicodeUTF8)

class CodeWindow(QtGui.QDialog):
    def __init__(self, messageWindow, codeCallback):
        QtGui.QDialog.__init__(self)

        self.ui=Ui_CodeWindow()
        self.ui.setupUi(self)

        # Setup signals
        self.ui.pushNo0.clicked.connect(self.pushNo0)
        self.ui.pushNo1.clicked.connect(self.pushNo1)
        self.ui.pushNo2.clicked.connect(self.pushNo2)
        self.ui.pushNo3.clicked.connect(self.pushNo3)
        self.ui.pushNo4.clicked.connect(self.pushNo4)
        self.ui.pushNo5.clicked.connect(self.pushNo5)
        self.ui.pushNo6.clicked.connect(self.pushNo6)
        self.ui.pushNo7.clicked.connect(self.pushNo7)
        self.ui.pushNo8.clicked.connect(self.pushNo8)
        self.ui.pushNo9.clicked.connect(self.pushNo9)
        self.ui.pushErase.clicked.connect(self.pushErase)
        self.ui.pushConfirm.clicked.connect(self.pushConfirm)
        self.ui.pushCancel.clicked.connect(self.pushCancel)

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.displayUpdate)
        self.timer.start(500)

        self.messageWindow = messageWindow
        self.codeCallback = codeCallback

        #
        self.ui.lineCode.setText("")
        self.ui.message.setText("Bitte Token eingeben...")

        self.lastInteraction = time.time()

    def exec_(self, code = ""):
        QtGui.QDialog.exec_(self)
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        #self.setWindowState(QtCore.Qt.WindowMaximized)
        self.ui.lineCode.setText(code)
        self.ui.message.setText("Bitte Token eingeben...")
        self.lastInteraction = time.time()

    def displayUpdate(self):
        t = time.time()

        # If no interaction is made, close this window
        if self.lastInteraction + CODE_INTERACTION_TIMEOUT < t:
            self.close()

    def pushNo(self, i):
        self.lastInteraction = time.time()
        t = self.ui.lineCode.text()
        t.append(str(i))
        self.ui.lineCode.setText(t)
        self.ui.message.setText("Bitte Token eingeben...")

    def pushErase(self):
        self.lastInteraction = time.time()
        t = self.ui.lineCode.text()
        self.ui.lineCode.setText(t[:-1])
        self.ui.message.setText("Bitte Token eingeben...")

    def pushConfirm(self):
        self.lastInteraction = time.time()
        self.codeCallback(self.ui.lineCode.text())

    def pushCancel(self):
        self.close()
    
    # Numpad logic...
    def pushNo0(self):
        self.pushNo(0)
    def pushNo1(self):
        self.pushNo(1)
    def pushNo2(self):
        self.pushNo(2)
    def pushNo3(self):
        self.pushNo(3)
    def pushNo4(self):
        self.pushNo(4)
    def pushNo5(self):
        self.pushNo(5)
    def pushNo6(self):
        self.pushNo(6)
    def pushNo7(self):
        self.pushNo(7)
    def pushNo8(self):
        self.pushNo(8)
    def pushNo9(self):
        self.pushNo(9)


