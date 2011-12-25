#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore
sys.path.insert(0, "RFIDIOt/")
sys.path.insert(0, "thirdparty/")
sys.path.insert(0, "coffeeprotocol/")

# Protocol
from coffeeprotocol import *

import config

# RFID
from RFID import *

# HTTPS Request
import httpsclient

# Main Window logic 
from mainWindow import *


class ClientProtocol(object):
    def __init__(self, server_url, server_pub):
        self.protocol = CoffeeProtocol()
        # HTTPS Client
        self.client = httpsclient.HTTPSClient(server_url, server_pub)

    def buildRequest(self, mifareid, cardid):
        return self.protocol.buildRequest(mifareid, cardid)

    def sendRequest(self, request):
        return self.protocol.parseResponse(self.client.makeRequest(request.compile('private.pem')))

def main():
    # Configuration
    cfg = config.Config(file("coffeesale.config"))
    rfid = RFIDdummy(cfg.rfid.key)

    # Protocol
    protocol = ClientProtocol("https://127.0.0.1:1443/", "server_pub.pem")

    # Init Qt App
    app = QtGui.QApplication(sys.argv)

    # Init Window
    window = MainWindow(rfid, protocol)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
