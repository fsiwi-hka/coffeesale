#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore
sys.path.insert(0, "RFIDIOt/")
sys.path.insert(0, "thirdparty/")

import config

# RFID
from RFID import *

# HTTPS Request
import httpsclient

# Main Window logic 
from mainWindow import *

def main():
    # Configuration
    cfg = config.Config(file("coffeesale.config"))
    rfid = RFIDdummy(cfg.rfid.key)

    # HTTPS Client
    client = httpsclient.HTTPSClient("https://127.0.0.1:1443/payment/", "server_pub.pem")

    # Init Qt App
    app = QtGui.QApplication(sys.argv)

    # Init Window
    window = MainWindow(rfid, client)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
