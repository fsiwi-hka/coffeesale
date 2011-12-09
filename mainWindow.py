#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os, json
from PyQt4 import QtGui, QtCore

from RFID import *

# Compiled ui classes
from mainUi import Ui_MainWindow

# Code window
from codeWindow import *

# Message window
from messageWindow import *

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

        # Message Window
        self.messageWindow = MessageWindow()

        # Code Window
        self.codeWindow = CodeWindow(self.messageWindow, client, self.redeemCode)
       

        # Business logic stuff
        self.lastInteraction = time.time()

        self.client = client
        self.rfid = rfid
        self.card = self.rfid.readCard()
        self.lastcard = None
        self.cardbalance = None
        
        self.displayTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.displayTimer, QtCore.SIGNAL("timeout()"), self.displayUpdate)
        self.displayUpdate()
        self.displayTimer.start(100)

        self.rfidTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.rfidTimer, QtCore.SIGNAL("timeout()"), self.rfidUpdate)
        self.rfidUpdate()
        self.rfidTimer.start(500)

    def rfidUpdate(self):
        #self.lastcard = self.card
        newcard = self.rfid.readCard()

        if newcard == None:
            self.lastcard = None
            self.card = None
            return

        if not newcard.isSame(self.lastcard):
            self.lastcard = self.card
            self.card = newcard

            balance = self.client.makeRequest(json.dumps({'mifareid':self.card.mifareid, 'cardid':self.card.cardid, 'action':'getBalance'}))

            self.card.balance = balance['balance']
            #self.cardbalance = self.client.makeRequest(json.dumps({'mifareid':self.mifareid, 'cardid':self.cardid, 'action':'getBalance'}))

            self.lastCard = self.card

        if self.card != None and self.card.used != True and (self.ui.pushCoffee.isChecked() or self.ui.pushClubMate.isChecked()):
            # buy item

            item = 0
            if self.ui.pushCoffee.isChecked():
                item = 1
            elif self.ui.pushClubMate.isChecked():
                item = 2


            if item > 0:
                self.ui.pushClubMate.setChecked(False)
                self.ui.pushCoffee.setChecked(False)

                # Save old balance
                oldBalance = self.card.balance                

                buy = self.client.makeRequest(json.dumps({'mifareid':self.card.mifareid, 'cardid':self.card.cardid, 'action':'buyItem', 'item':str(item)}))
                if buy['success'] == "False":
                    self.messageWindow.show("Junge nicht genug geld\nSuch dir nen Job\nScheiss Hippi :3", 3)
                    return

                # Mark this card as used, you cant buy any items with this card anymore 
                self.card.used = True
                
                balance = self.client.makeRequest(json.dumps({'mifareid':self.card.mifareid, 'cardid':self.card.cardid, 'action':'getBalance'}))
                self.card.balance = balance['balance']

                message = "Item gekauft\n\n"
                message += "Altes Guthaben: " + str(oldBalance) + "€\n\n"
                message += "Neues Guthaben: " + str(self.card.balance) + "€"
                message = QtGui.QApplication.translate("", message, None, QtGui.QApplication.UnicodeUTF8)

                self.messageWindow.show(message, 3)

                return
        return

    def redeemCode(self, code):
        if self.card == None or self.card.used == True:
            self.codeWindow.ui.message.setText("No Card?")
            return

        oldBalance = self.card.balance                

        redeem = self.client.makeRequest(json.dumps({'mifareid':self.card.mifareid, 'cardid':self.card.cardid, 'action':'redeemToken', 'token':str(code)}))
        if redeem['success'] == "False":
            self.codeWindow.ui.message.setText("Token Falsch! :(")
            return
    
        balance = self.client.makeRequest(json.dumps({'mifareid':self.card.mifareid, 'cardid':self.card.cardid, 'action':'getBalance'}))
        self.card.balance = balance['balance']
    
        self.codeWindow.close()

        message = "Code eingelöst\n\n"
        message += "Altes Guthaben: " + str(oldBalance) + "€\n\n"
        message += "Neues Guthaben: " + str(self.card.balance) + "€"
        message = QtGui.QApplication.translate("", message, None, QtGui.QApplication.UnicodeUTF8)

        self.messageWindow.show(message, 3)

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

        if self.card != None and self.card.used != True:
            cardtext = "Guthaben: " + str(self.card.balance) + EURO
        elif price != "":
            cardtext += " - " + price

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

