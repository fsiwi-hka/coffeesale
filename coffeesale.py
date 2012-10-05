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
    def __init__(self, server_url, server_pub, client_priv):
        self.protocol = CoffeeProtocol()
        self.client_priv = client_priv
        # HTTPS Client
        self.client = httpsclient.HTTPSClient(server_url, server_pub)

    def buildRequest(self, mifareid, cardid):
        return self.protocol.buildRequest(mifareid, cardid)

    def sendRequest(self, request):
        return self.protocol.parseResponse(self.client.jsonRequest(request.compile(self.client_priv)))

    def getRequest(self, url):
        return self.client.getRequest(url)

def main():
    # Configuration
    cfg = config.Config(file("coffeesale.config"))

    if not cfg.client.use_rfid_dummy:
        rfid = RFID(cfg.rfid.key)
    else:
        rfid = RFIDdummy(cfg.rfid.key)

    # Protocol
    protocol = ClientProtocol(cfg.client.server_url, cfg.client.server_pub, cfg.client.private_key)

    # Init Qt App
    app = QtGui.QApplication(sys.argv)

    if cfg.client.hide_cursor:
        app.setOverrideCursor(QtGui.QCursor(10));

    # Init Window
    window = MainWindow(rfid, protocol, cfg)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
