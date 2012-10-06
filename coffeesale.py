#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore
sys.path.insert(0, "RFIDIOt/")
sys.path.insert(0, "thirdparty/")
sys.path.insert(0, "coffeeprotocol/")

# Protocol
from coffeeprotocol import *

# Config
import config

# RFID
from RFID import *

# HTTPS Request
import httpsclient

# Main Window logic 
from mainWindow import *

# Message window
from messageWindow import *

class Struct:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

class ClientProtocol(object):
    def __init__(self, server_url, server_pub, client_priv):
        self.protocol = CoffeeProtocol()
        self.client_priv = client_priv

        # Message Window
        self.messageWindow = MessageWindow()

        # HTTPS Client
        self.client = httpsclient.HTTPSClient(server_url, server_pub)

    def buildRequest(self, mifareid, cardid):
        return self.protocol.buildRequest(mifareid, cardid)

    def sendRequest(self, request):
        success = False
        tries = 0
        while success is not True:
            try:
                response = self.client.jsonRequest(request.compile(self.client_priv))
                success = True
            except:
                tries += 1
                self.messageWindow.show("Could not reach server, retrying (" + str(tries) + ") ...", 99999)
                QtCore.QCoreApplication.processEvents()
                time.sleep(1)
                
        self.messageWindow.close()
        return self.protocol.parseResponse(response)

    def getRequest(self, url):
        #return self.client.getRequest(url)
        success = False
        tries = 0
        while success is not True:
            try:
                response = self.client.getRequest(url)
                success = True
            except:
                tries += 1
                self.messageWindow.show("Could not reach server, retrying (" + str(tries) + ") ...", 99999)
                QtCore.QCoreApplication.processEvents()
                time.sleep(1)
                
        self.messageWindow.close()
        return response

def main():
    # Configuration
    cfg = config.Config(file("coffeesale.config"))

    if not cfg.client.use_rfid_dummy:
        rfid = RFID(cfg.rfid.key)
    else:
        rfid = RFIDdummy(cfg.rfid.key)

    # Init Qt App
    app = QtGui.QApplication(sys.argv)

    # Protocol
    protocol = ClientProtocol(cfg.client.server_url, cfg.client.server_pub, cfg.client.private_key)

    if cfg.client.hide_cursor:
        app.setOverrideCursor(QtGui.QCursor(10));

    # Init Window
    window = MainWindow(rfid, protocol, cfg)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
