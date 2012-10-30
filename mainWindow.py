#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os, json, urllib
from functools import partial
from PyQt4 import QtGui, QtCore
import pygame

from RFID import *

# Compiled ui classes
from mainUi import Ui_MainWindow

# Windows
from codeWindow import *
from messageWindow import *
from tosWindow import *
from screensaverWindow import *
from adminWindow import *

# CoffeeClient
from coffeeclient import *

class MainWindow(QtGui.QMainWindow):
    def __init__(self, cfg):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.cfg = cfg
        self.show()

        # Initialize sound output
        pygame.mixer.init()

        # Message Window
        self.messageWindow = MessageWindow(self)
        self.messageWindow.show("Just a moment...", 999999)
        QtCore.QCoreApplication.processEvents()
        
        # Windows
        self.codeWindow = CodeWindow(self.messageWindow, self.redeemCode, self)
        self.tosWindow = TosWindow(self)
        self.screensaverWindow = ScreensaverWindow(self)
        self.adminWindow = AdminWindow(self)

        # RFID reading
        if not cfg.client.use_rfid_dummy:
            self.rfid = RFIDWorker(cfg.rfid.key)
        else:
            self.rfid = RFIDDummyWorker(cfg.rfid.key)
        self.connect(self.rfid, SIGNAL("cardRead(PyQt_PyObject)"), self.rfidUpdate)
        self.rfid.start()
 
        # Business logic stuff
        self.client = CoffeeClient()
        self.card = self.rfid.readCard()
        self.wallet = None
        self.user = None
        self.lastcard = None
        self.adminButton = None
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
        QtCore.QObject.connect(self.itemsTimer, QtCore.SIGNAL("timeout()"), self.rebuildItemTimeout)
        self.rebuildItems()
        self.itemsTimer.setInterval(cfg.client.item_refresh)
        self.itemsTimer.start()
        
        # Click event for message label
        self.ui.message.mousePressEvent = self.onMessageLabelClicked

    def rebuildItemTimeout(self):
        if self.card is None:
            self.rebuildItems()

    def rebuildItems(self):
        self.messageWindow.show("Items werden geupdated ...", 999999)
        print "Rebuilding items...", 

        QtCore.QCoreApplication.processEvents()

        # Remove all buttons
        for i in range(self.ui.dynamicButtonLayout.count()): 
            self.ui.dynamicButtonLayout.itemAt(i).widget().deleteLater()
            self.ui.dynamicButtonLayout.itemAt(i).widget().close()

        self.buttons = {}
        
        # Add new buttons
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setWeight(75)
        font.setBold(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        items = sorted(self.client.getItems(), cmp=Item_Sort)

        rows = 1

        if items is None:
            items = []

        self.items = {} 

        orderIndex = 0
        for item in items:
            self.items[item.id] = item

            # Download the item icon
            f = open("resource/items/" + str(item.id) + ".png", "w+")
            f.write(self.client.getRequest("resource/item/" + str(item.id)))
            f.close()

            if item.enabled != True:
                continue

            button = QtGui.QPushButton(self.ui.centralwidget)
            button.setSizePolicy(sizePolicy)
            button.setFont(font)
            button.setStyleSheet("image: url(resource/items/" + str(item.id) + ".png);")
            button.setCheckable(True)
            button.setObjectName(item.desc)
    
            if item.sold_out:
                button.setText(item.desc + "\nAusverkauft")
                button.setEnabled(False)
            else:
                button.setText(item.desc + " / " + str(item.price) + " Bits")
                button.setEnabled(True)

            self.ui.dynamicButtonLayout.addWidget(button, 0, orderIndex)
            orderIndex += 1
            button.clicked.connect(partial(self.pushItemClicked, item.id))
            self.buttons[item.id] = button
            QtCore.QCoreApplication.processEvents()

        # Charge button...
        self.chargeButton = QtGui.QPushButton(self.ui.centralwidget)
        self.chargeButton.setSizePolicy(sizePolicy)
        self.chargeButton.setFont(font)
        self.chargeButton.setStyleSheet("image: url(resource/gold.png);")
        self.chargeButton.setObjectName("Aufladen")
        self.chargeButton.setText("Aufladen")
        self.ui.dynamicButtonLayout.addWidget(self.chargeButton, 0, 1337, rows, 1)
        self.chargeButton.clicked.connect(self.pushChargeClicked)
 
        self.adminButton = QtGui.QPushButton(self.ui.centralwidget)
        self.adminButton.setSizePolicy(sizePolicy)
        self.adminButton.setFont(font)
        self.adminButton.setStyleSheet("image: url(resource/admin.png);")
        self.adminButton.setObjectName("Admin")
        self.adminButton.setText("Admin")
        self.adminButton.setVisible(False)
        self.ui.dynamicButtonLayout.addWidget(self.adminButton, 0, 1338, rows, 1)
        self.adminButton.clicked.connect(self.pushAdminClicked)
         
        print "done"
        QtCore.QCoreApplication.processEvents()
        self.messageWindow.show("Items werden geupdated ...", 1)
        self.displayUpdate()

    def rfidUpdate(self, newcard):
        #self.lastcard = self.card
        #newcard = self.rfid.readCard()

        if newcard == None:
            self.lastcard = None
            self.card = None
            self.wallet = None
            self.user = None
            CoffeeClient().resetIds()
            self.closeAllWindows()
            self.displayUpdate()
            return

        if not newcard.isSame(self.lastcard):
            self.resetScreensaverTimeout()
            self.resetInteractionTimeout()
            self.closeAllWindows()

            self.lastcard = self.card
            self.card = newcard

            CoffeeClient().setIds(self.card.mifareid, self.card.cardid)
            self.wallet = CoffeeClient().getWallet()

            self.user = None
            if self.wallet != None:
                self.card.valid = True
                self.user = CoffeeClient().getUser()

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
            oldBalance = 0
            
            if self.wallet is not None:
                oldBalance = self.wallet.balance
          
            buyReq = CoffeeClient().buyItem(item)

            if buyReq == False:
                self.messageWindow.show("Nicht genug Bits.", 4)
                return
           
            self.wallet = CoffeeClient().getWallet()

            message = str(self.items[item].desc) + " gekauft\n\n"
            message += "Altes Guthaben: " + str(oldBalance) + " Bits\n"
            message += "Neues Guthaben: " + str(self.wallet.balance)+ " Bits\n\n"
            message = QtGui.QApplication.translate("", message, None, QtGui.QApplication.UnicodeUTF8)

            self.messageWindow.show(message, 4)
        self.displayUpdate()

    def redeemCode(self, token):
        code = token

        if self.card == None:
            self.codeWindow.ui.message.setText("Karte nicht angelegt?")
            return

        oldBalance = 0
        
        if self.wallet is not None:
            oldBalance = self.wallet.balance

        redeemResp = CoffeeClient().redeemToken(code)

        if redeemResp == False:
            self.codeWindow.ui.message.setText("Token ist falsch.")
            return
       
        self.wallet = CoffeeClient().getWallet()
        self.codeWindow.accept()

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
        self.screensaverWindow.close()
        self.screensaverTimer.stop()
        self.screensaverTimer.start()

    def resetInteractionTimeout(self):
        self.interactionTimer.stop()
        self.interactionTimer.start()

    def screensaverTimeout(self):
        if self.card is None:
            self.interactionTimeout()
            self.screensaverWindow.show()

    def interactionTimeout(self):
        if self.card is not None and self.user is not None:
            return

        for i in self.buttons:
            self.buttons[i].setChecked(False)
        self.closeAllWindows()

    def closeAllWindows(self):
        self.tosWindow.close()
        self.codeWindow.close()
        self.adminWindow.close()
        self.tosWindow.close()
        self.messageWindow.close()

    def displayUpdate(self):
        cardtext = "Bitte Karte anlegen ..."
        price = ""
       
        if self.adminButton is not None:
            self.adminButton.setVisible((self.user != None and self.user.admin == True))
        
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

        if self.wallet is not None:
            self.buttons[id].setChecked(True)

        self.displayUpdate()

    def pushChargeClicked(self):
        self.resetInteractionTimeout()
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
        if self.user is not None and self.user.admin is True:
            self.itemsTimer.stop()
            self.screensaverTimer.stop()
            self.interactionTimer.stop()
            self.adminWindow.exec_()
            self.interactionTimer.start()
            self.screensaverTimer.start()
            self.itemsTimer.start()
            self.rebuildItems()
        return

    def onMessageLabelClicked(self, event):
        self.resetScreensaverTimeout()
        try:
            if self.card is not None:
                if self.card.ccBalance != None or False == True:
                    s = "CampusCard\n\nAktuelles Guthaben: %0.2f Euro\nLetztes Guthaben: %0.2f Euro" % (self.card.ccBalance, self.card.ccLastBalance)
                    self.messageWindow.show(s, 5)
        except:
            pass

    def keyPressEvent(self, e):            
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
