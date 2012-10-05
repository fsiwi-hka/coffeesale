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
    def __init__(self, rfid, protocol, cfg):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.cfg = cfg
        #self.show()

        # Read some config stuff
        self.screensaver_timeout = cfg.client.screensaver_timeout
        self.interaction_timeout = cfg.client.interaction_timeout

        # Initialize sound output
        pygame.mixer.init()

        # Message Window
        self.messageWindow = MessageWindow()

        # Code Window
        self.codeWindow = CodeWindow(self.messageWindow, self.redeemCode)

        # TOS Window
        self.tosWindow = TosWindow()

        # Screensaver
        self.screensaver = ScreensaverWindow()

        # Business logic stuff
        self.lastInteraction = time.time()
        self.lastAction = time.time()

        self.protocol = protocol
        self.rfid = rfid
        self.card = self.rfid.readCard()
        self.lastcard = None
        self.cardbalance = None
        self.buttons = {}
        self.items = {}

        # Close message window, we are done
        self.messageWindow.close()
 
        # Timer for item updates
        self.itemsTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.itemsTimer, QtCore.SIGNAL("timeout()"), self.rebuildItems)
        self.rebuildItems()
        self.itemsTimer.setInterval(cfg.client.item_refresh)
        self.itemsTimer.start()
        
        # Timer for display updates
        self.displayTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.displayTimer, QtCore.SIGNAL("timeout()"), self.displayUpdate)
        self.displayUpdate()
        self.displayTimer.setInterval(cfg.client.display_refresh)
        self.displayTimer.start()
        
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
        
        req = self.protocol.buildRequest(0, 0)
        req.action = "getItems"
        resp = self.protocol.sendRequest(req)

        #self.items = resp.data['items']
        for item in resp.data['items']:
            self.items[item['id']] = item
            f = open("resource/items/" + str(item['id']) + ".png", "w+")
            f.write(self.protocol.getRequest("resource/item/" + str(item['id'])))
            f.close()

            button = QtGui.QPushButton(self.ui.centralwidget)
            button.setSizePolicy(sizePolicy)
            button.setFont(font)
            button.setStyleSheet("image: url(resource/items/" + str(item['id']) + ".png);")
            button.setCheckable(True)
            button.setObjectName(item['desc'])
            button.setText(item['desc'] + " / " + str(item['price']) + " Bits")
            self.ui.buttonLayout.addWidget(button)
            button.clicked.connect(partial(self.pushItemClicked, item['id']))
            self.buttons[item['id']] = button

        # Charge button...
        button = QtGui.QPushButton(self.ui.centralwidget)
        button.setSizePolicy(sizePolicy)
        button.setFont(font)
        button.setStyleSheet("image: url(resource/gold.png);")
        button.setObjectName("Aufladen")
        button.setText("Aufladen")
        self.ui.buttonLayout.addWidget(button)
        button.clicked.connect(self.pushChargeClicked)
        #self.buttons[-1] = button
        print "done."
        self.messageWindow.close()
        self.displayUpdate()

    def rfidUpdate(self):
        #self.lastcard = self.card
        newcard = self.rfid.readCard()

        if newcard == None:
            self.lastcard = None
            self.card = None
            self.messageWindow.close()
            return

        if not newcard.isSame(self.lastcard):
            self.screensaver.close()
            self.lastAction = time.time()

            self.lastcard = self.card
            self.card = newcard

            balanceReq = self.protocol.buildRequest(self.card.mifareid, self.card.cardid)
            balanceReq.action = "getBalance"
            balanceResp = self.protocol.sendRequest(balanceReq) 
            self.card.balance = balanceResp.data['balance']

            if balanceResp.success:
                self.card.valid = True

            self.lastCard = self.card
        
        item = 0
        for i in self.buttons:
            if self.buttons[i].isChecked():
                item = i

        if self.card != None and self.card.used != True and item > 0:
            # buy item
            for i in self.buttons:
                self.buttons[i].setChecked(False)

            # Save old balance
            oldBalance = self.card.balance                
            
            buyReq = self.protocol.buildRequest(self.card.mifareid, self.card.cardid)
            buyReq.action = "buyItem"
            buyReq.data['item'] = str(item)
            buyResp = self.protocol.sendRequest(buyReq) 

            if buyResp.success == False:
                self.messageWindow.show("Nicht genug Bits.", 3)
                return

            # Mark this card as used, you cant buy any items with this card anymore 
            #self.card.used = True
            
            balanceReq = self.protocol.buildRequest(self.card.mifareid, self.card.cardid)
            balanceReq.action = "getBalance"
            balanceResp = self.protocol.sendRequest(balanceReq) 
            self.card.balance = balanceResp.data['balance']               

            message = str(self.items[item]['desc']) + " gekauft\n\n"
            message += "Altes Guthaben: " + str(oldBalance) + " Bits\n"
            message += "Neues Guthaben: " + str(self.card.balance)+ " Bits\n\n"
            message = QtGui.QApplication.translate("", message, None, QtGui.QApplication.UnicodeUTF8)

            self.messageWindow.show(message, 4)

    def redeemCode(self, code):
        if self.card == None or self.card.used == True:
            self.codeWindow.ui.message.setText("Karte nicht angelegt?")
            return

        oldBalance = self.card.balance                

        redeemReq = self.protocol.buildRequest(self.card.mifareid, self.card.cardid)
        redeemReq.action = "redeemToken"
        redeemReq.data['token'] = str(code)
        redeemResp = self.protocol.sendRequest(redeemReq) 

        if redeemResp.success == False:
            self.codeWindow.ui.message.setText("Token Falsch! :(")
            return
        
        balanceReq = self.protocol.buildRequest(self.card.mifareid, self.card.cardid)
        balanceReq.action = "getBalance"
        balanceResp = self.protocol.sendRequest(balanceReq) 
        self.card.balance = balanceResp.data['balance']
    
        self.codeWindow.close()

        # Plays beep
        pygame.mixer.music.load("resource/beep.wav")
        pygame.mixer.music.play()

        message = "Code eingelöst\n\n"
 
        message += "Altes Guthaben: " + str(oldBalance) + " Bits\n\n"
        message += "Neues Guthaben: " + str(self.card.balance)+ " Bits\n\n"
        message = QtGui.QApplication.translate("", message, None, QtGui.QApplication.UnicodeUTF8)

        self.messageWindow.show(message, 4)

        # update rfid
        self.card.valid = True
        self.rfidUpdate()
        

    def displayUpdate(self):
        t = time.time()

        if self.lastAction + self.screensaver_timeout < t:
            self.lastAction = t
            self.screensaver.show()

        # Reset selection if no interaction is made after specified time
        if self.lastInteraction + self.interaction_timeout < t and self.card == None:
            self.lastInteraction = t
            for i in self.buttons:
                self.buttons[i].setChecked(False)
        
        cardtext = "Bitte Karte anlegen ..."
        price = ""
        
        for i in self.buttons:
            if self.buttons[i].isChecked():
                price = self.items[i]['desc'] + " a " + str(self.items[i]['price']) + " Bits"

        if self.card != None and self.card.used != True:
            cardtext = "Guthaben: " + str(self.card.balance) + " Bits"
        elif price != "":
            cardtext += " - " + price

        messagetext = cardtext

        self.ui.message.setText(messagetext)

    def pushItemClicked(self, id):
        self.lastInteraction = time.time()
        for i in self.buttons:
            self.buttons[i].setChecked(False)

        self.buttons[id].setChecked(True)

    def pushChargeClicked(self):
        self.lastInteraction = 0
        if self.card:
            if not self.card.valid:
                if self.tosWindow.exec_() == 0:
                    return
            self.codeWindow.exec_()

    def keyPressEvent(self, e):            
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
