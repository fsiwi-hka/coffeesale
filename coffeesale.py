#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore
sys.path.insert(0, "RFIDIOt/")
sys.path.insert(0, "thirdparty/")

import config

# RFIDIOt library
import RFIDIOtconfig

# HTTPS Request
import httpsclient

# Main Window logic 
from mainWindow import *

class RFIDHelper(object):
    def __init__(self):

        cfg = config.Config(file("coffeesale.config"))
        self.key = cfg.rfid.key
        try:
            self.card = RFIDIOtconfig.card
        except:
            os._exit(False)
    
    def readCard(self):
        if not self.card.select():
            return None

        cardid = -1
        mifareid = -1
        try:
            cardid = int(self.card.uid[1:], 16)
            self.card.select()
            if self.card.login(44/4, 'AA', self.key):
                self.card.readMIFAREblock(44)
                mifareid = long(self.card.ReadablePrint(self.card.ToBinary(self.card.MIFAREdata))[:-4])
            else:
                return None
        except:
            return None

        if cardid == -1 or mifareid == -1:
            return None

        return [cardid, mifareid]

def main():
    rfid = RFIDHelper()
    client = httpsclient.HTTPSClient("https://127.0.0.1:1443/payment/", "server_pub.pem")
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(rfid, client)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
