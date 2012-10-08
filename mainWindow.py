#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os, json, urllib
from functools import partial
from PyQt4 import QtGui, QtCore
import pygame

from RFID import *

# Compiled ui classes
from mainUi import Ui_MainWindow

# Code window
from codeWindow import *

# Message window
from messageWindow import *

# TOS Window
from tosWindow import *

# Screensaver
from screensaverWindow import *

class MainWindow(QtGui.QMainWindow):
    def __init__(self, rfid, client, cfg):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.cfg = cfg
        self.show()

        # Initialize sound output
        pygame.mixer.init()

        # Message Window
        self.messageWindow = MessageWindow()
        self.messageWindow.show("Just a moment...", 999999)
        QtCore.QCoreApplication.processEvents()
        
        # Code Window
        self.codeWindow = CodeWindow(self.messageWindow, self.redeemCode)

        # TOS Window
        self.tosWindow = TosWindow()

        # Screensaver
        self.screensaver = ScreensaverWindow()

        # Business logic stuff
        self.client = client
        self.rfid = rfid
        self.card = self.rfid.readCard()
        self.wallet = None
        self.lastcard = None
        self.buttons = {}
        self.items = {}

        # Close message window, we are done
        self.messageWindow.close()
 
        # Timer for screensaver timeouts
        self.screensaverTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.screensaverTimer, QtCore.SIGNAL("timeout()"), self.screensaverTimeout)
        self.screensaverTimer.setInterval(cfg.client.screensaver_timeout * 1000)
        self.screensaverTimer.start()

         # Timer for interaction timeouts
        self.interactionTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.interactionTimer, QtCore.SIGNAL("timeout()"), self.interactionTimeout)
        self.interactionTimer.setInterval(cfg.client.interaction_timeout * 1000)
        self.interactionTimer.start()
 
        # Timer for item updates
        self.itemsTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.itemsTimer, QtCore.SIGNAL("timeout()"), self.rebuildItems)
        self.rebuildItems()
        self.itemsTimer.setInterval(cfg.client.item_refresh)
        self.itemsTimer.start()
        
        # Timer for rfid updates
        self.rfidTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.rfidTimer, QtCore.SIGNAL("timeout()"), self.rfidUpdate)
        self.rfidUpdate()
        self.rfidTimer.setInterval(cfg.client.rfid_refresh)
        self.rfidTimer.start()
 
    def rebuildItems(self):
        self.messageWindow.show("Just a moment...", 999999)
        self.ui.message.setText("Rebuilding items")
        print "Rebuilding items...", 

        QtCore.QCoreApplication.processEvents()

        # Remove all buttons
        for i in range(self.ui.buttonLayout.count()): 
            self.ui.buttonLayout.itemAt(i).widget().close()

        self.buttons = {}
        
        # Add new buttons
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setWeight(75)
        font.setBold(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        
        items = self.client.getItems() 

        if items is None:
            items = []

        self.items = {} 
        #self.items = resp.data['items']
        for item in items:
            self.items[item.id] = item
            f = open("resource/items/" + str(item.id) + ".png", "w+")
            f.write(self.client.getRequest("resource/item/" + str(item.id)))
            f.close()

            button = QtGui.QPushButton(self.ui.centralwidget)
            button.setSizePolicy(sizePolicy)
            button.setFont(font)
            button.setStyleSheet("image: url(resource/items/" + str(item.id) + ".png);")
            button.setCheckable(True)
            button.setObjectName(item.desc)
            button.setText(item.desc + " / " + str(item.price) + " Bits")
            self.ui.buttonLayout.addWidget(button)
            button.clicked.connect(partial(self.pushItemClicked, item.id))
            self.buttons[item.id] = button

        # Charge button...
        self.chargeButton = QtGui.QPushButton(self.ui.centralwidget)
        self.chargeButton.setSizePolicy(sizePolicy)
        self.chargeButton.setFont(font)
        self.chargeButton.setStyleSheet("image: url(resource/gold.png);")
        self.chargeButton.setObjectName("Aufladen")
        self.chargeButton.setText("Aufladen")
        self.ui.buttonLayout.addWidget(self.chargeButton)
        self.chargeButton.clicked.connect(self.pushChargeClicked)
 
        self.adminButton = QtGui.QPushButton(self.ui.centralwidget)
        self.adminButton.setSizePolicy(sizePolicy)
        self.adminButton.setFont(font)
        self.adminButton.setStyleSheet("image: url(resource/gold.png);")
        self.adminButton.setObjectName("Admin")
        self.adminButton.setText("Admin")
        self.adminButton.setVisible(False)
        self.ui.buttonLayout.addWidget(self.adminButton)
        self.adminButton.clicked.connect(self.pushAdminClicked)
         
        print "done"
        self.messageWindow.close()
        self.displayUpdate()

    def rfidUpdate(self):
        #self.lastcard = self.card
        newcard = self.rfid.readCard()

        if newcard == None:
            self.lastcard = None
            self.card = None
            self.wallet = None
            self.messageWindow.close()
            self.displayUpdate()
            return

        if not newcard.isSame(self.lastcard):
            self.screensaver.close()
            #self.resetInteractionTimeout()

            self.lastcard = self.card
            self.card = newcard

            self.wallet = self.client.getWallet(self.card.mifareid, self.card.cardid)

            if self.wallet != None:
                self.card.valid = True

            self.lastcard = self.card
        
        item = 0
        for i in self.buttons:
            if self.buttons[i].isChecked():
                item = i

        if self.card != None and item > 0:
            # buy item
            for i in self.buttons:
                self.buttons[i].setChecked(False)

            # Save old balance
            oldBalance = self.wallet.balance
          
            buyReq = self.client.buyItem(item, self.card.mifareid, self.card.cardid)

            if buyReq == False:
                self.messageWindow.show("Nicht genug Bits.", 3)
                return
           
            self.wallet = self.client.getWallet(self.card.mifareid, self.card.cardid)

            message = str(self.items[item].desc) + " gekauft\n\n"
            message += "Altes Guthaben: " + str(oldBalance) + " Bits\n"
            message += "Neues Guthaben: " + str(self.wallet.balance)+ " Bits\n\n"
            message = QtGui.QApplication.translate("", message, None, QtGui.QApplication.UnicodeUTF8)

            self.messageWindow.show(message, 4)
        self.displayUpdate()

    def redeemCode(self, code):
        if self.card == None:
            self.codeWindow.ui.message.setText("Karte nicht angelegt?")
            return

        oldBalance = 0
        
        if self.wallet is not None:
            oldBalance = self.wallet.balance

        redeemResp = self.client.redeemToken(int(code), self.card.mifareid, self.card.cardid)

        if redeemResp == False:
            self.codeWindow.ui.message.setText("Token Falsch! :(")
            return
       
        self.wallet = self.client.getWallet(self.card.mifareid, self.card.cardid)
        self.codeWindow.close()

        # Plays beep
        pygame.mixer.music.load("resource/beep.wav")
        pygame.mixer.music.play()

        message = "Code eingelöst\n\n"
 
        message += "Altes Guthaben: " + str(oldBalance) + " Bits\n\n"
        message += "Neues Guthaben: " + str(self.wallet.balance)+ " Bits\n\n"
        message = QtGui.QApplication.translate("", message, None, QtGui.QApplication.UnicodeUTF8)

        self.messageWindow.show(message, 4)

        # update rfid
        self.card.valid = True
        self.rfidUpdate()

    def resetScreensaverTimeout(self):
        self.screensaverTimer.stop()
        self.screensaverTimer.start()

    def resetInteractionTimeout(self):
        self.interactionTimer.stop()
        self.interactionTimer.start()

    def screensaverTimeout(self):
        self.screensaver.show()

    def interactionTimeout(self):
        for i in self.buttons:
            self.buttons[i].setChecked(False)

    def displayUpdate(self):
        cardtext = "Bitte Karte anlegen ..."
        price = ""
        
        self.adminButton.setVisible(False)
        
        for i in self.buttons:
            if self.buttons[i].isChecked():
                price = self.items[i].desc + " a " + str(self.items[i].price) + " Bits"

        if self.card != None:
            if self.wallet != None:
                cardtext = "Guthaben: " + str(self.wallet.balance) + " Bits"
            else:
                cardtext = "Guthaben: 0 Bits"
        elif price != "":
            cardtext += " - " + price

        messagetext = cardtext
        self.ui.message.setText(messagetext)

    def pushItemClicked(self, id):
        self.resetInteractionTimeout()
        self.resetScreensaverTimeout()
        for i in self.buttons:
            self.buttons[i].setChecked(False)

        self.buttons[id].setChecked(True)
        self.displayUpdate()

    def pushChargeClicked(self):
        self.resetInteractionTimeout()
        self.interactionTimeout()
        self.screensaverTimer.stop()
        if self.card:
            if not self.card.valid:
                if self.tosWindow.exec_() == 0:
                    self.screensaverTimer.start()
                    return
            self.codeWindow.exec_()
        self.displayUpdate()
        self.screensaverTimer.start()

    def pushAdminClicked(self):
        return

    def keyPressEvent(self, e):            
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
