# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'coffee.ui'
#
# Created: Tue Dec  6 12:01:30 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(530, 405)
        MainWindow.setStyleSheet(_fromUtf8("QMainWindow {\n"
"    background-color: #FCFCFC;\n"
"}\n"
"\n"
"QLabel#message {\n"
"    color: white;\n"
"    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(52, 161, 224, 255), stop:1 rgba(36, 110, 153, 255));\n"
"    border-radius: 1em;\n"
"    padding: 1em;\n"
"    font-size: 20px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"#logo {\n"
"    image: url(resource/logo.png);\n"
"}\n"
"\n"
"QPushButton, QToolButton {\n"
"    border: 4px solid #CCC;\n"
"    border-radius: 0.5em;\n"
"    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(212, 212, 212, 255));\n"
"    text-align: bottom center;\n"
"    padding: 0.3em;\n"
"}\n"
"\n"
"QPushButton:on, QToolButton:on {\n"
"    border-color: #85c441;\n"
"    background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(212, 212, 212, 255));\n"
"\n"
"}"))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.logo = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logo.sizePolicy().hasHeightForWidth())
        self.logo.setSizePolicy(sizePolicy)
        self.logo.setMinimumSize(QtCore.QSize(0, 140))
        self.logo.setText(_fromUtf8(""))
        self.logo.setObjectName(_fromUtf8("logo"))
        self.verticalLayout.addWidget(self.logo)
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setContentsMargins(5, -1, 5, -1)
        self.buttonLayout.setObjectName(_fromUtf8("buttonLayout"))
        self.btCoffee = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btCoffee.sizePolicy().hasHeightForWidth())
        self.btCoffee.setSizePolicy(sizePolicy)
        self.btCoffee.setStyleSheet(_fromUtf8("image: url(resource/coffee.png);"))
        self.btCoffee.setCheckable(True)
        self.btCoffee.setObjectName(_fromUtf8("btCoffee"))
        self.buttonLayout.addWidget(self.btCoffee)
        self.btMate = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btMate.sizePolicy().hasHeightForWidth())
        self.btMate.setSizePolicy(sizePolicy)
        self.btMate.setCheckable(True)
        self.btMate.setObjectName(_fromUtf8("btMate"))
        self.buttonLayout.addWidget(self.btMate)
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.buttonLayout.addWidget(self.pushButton_2)
        self.btAufladen = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btAufladen.sizePolicy().hasHeightForWidth())
        self.btAufladen.setSizePolicy(sizePolicy)
        self.btAufladen.setObjectName(_fromUtf8("btAufladen"))
        self.btAufladen.setStyleSheet(_fromUtf8("image: url(resource/gold.jpg);"))
        self.buttonLayout.addWidget(self.btAufladen)
        self.verticalLayout.addLayout(self.buttonLayout)
        self.message = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.message.sizePolicy().hasHeightForWidth())
        self.message.setSizePolicy(sizePolicy)
        self.message.setObjectName(_fromUtf8("message"))
        self.verticalLayout.addWidget(self.message)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.btCoffee.setText(QtGui.QApplication.translate("MainWindow", "Kaffee / 0,50€", None, QtGui.QApplication.UnicodeUTF8))
        self.btMate.setText(QtGui.QApplication.translate("MainWindow", "Club Mate / 1,50€", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("MainWindow", "Becher / 0,10€", None, QtGui.QApplication.UnicodeUTF8))
        self.btAufladen.setText(QtGui.QApplication.translate("MainWindow", "Aufladen", None, QtGui.QApplication.UnicodeUTF8))
        self.message.setText(QtGui.QApplication.translate("MainWindow", "Bitte Karte auflegen ...", None, QtGui.QApplication.UnicodeUTF8))

import coffee_rc
