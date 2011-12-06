#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os, json
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
    def __init__(self, rfid, client):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        # Setup signals
        self.ui.pushCoffee.clicked.connect(self.pushCoffeeClicked)
        self.ui.pushClubMate.clicked.connect(self.pushMateClicked)
        self.ui.pushCharge.clicked.connect(self.pushChargeClicked)

        # Code Window
        self.codeWindow = CodeWindow()
        self.codeWindow.setModal(True)
        
        # Business logic stuff
        self.lastInteraction = time.time()

        self.client = client
        self.rfid = rfid
        self.card = self.rfid.readCard()
        self.lastCard = None
        
        self.displayTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.displayTimer, QtCore.SIGNAL("timeout()"), self.displayUpdate)
        self.displayUpdate()
        self.displayTimer.start(100)

        self.rfidTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.rfidTimer, QtCore.SIGNAL("timeout()"), self.rfidUpdate)
        self.rfidUpdate()
        self.rfidTimer.start(700)

    def rfidUpdate(self):
        self.card = self.rfid.readCard()

        if self.card != self.lastCard:
            self.lastCard = self.card


    def displayUpdate(self):
        t = time.time()

        # Reset selection if no interaction is made after specified time
        if self.lastInteraction + MAIN_INTERACTION_TIMEOUT < t and self.card == None:
            self.lastInteraction = t
            self.ui.pushClubMate.setChecked(False)
            self.ui.pushCoffee.setChecked(False)
        
        cardtext = "Bitte Karte anlegen ..."
        price = ""
        if self.ui.pushCoffee.isChecked():
            price = "Kaffee a 0,50" + EURO
        elif self.ui.pushClubMate.isChecked():
            price = "Club Mate a 1,50" + EURO

        if self.card != None:
            balance = self.client.makeRequest(json.dumps({'mifareid':self.card[0], 'cardid':self.card[1], 'action':'getBalance'}))
            print balance
            sys.exit(0)
            cardtext = "Guthaben: " + str(balance)

        messagetext = cardtext
        #if price != "":
        #    messagetext += " - " + price

        self.ui.message.setText(messagetext)

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

