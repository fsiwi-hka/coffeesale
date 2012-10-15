#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore
sys.path.insert(0, "RFIDIOt/")
sys.path.insert(0, "thirdparty/")
sys.path.insert(0, "coffeeprotocol/")

# Config
import config

# RFID
from RFID import *

# Main Window logic 
from mainWindow import *

# Coffeeclient
from coffeeclient import *

def main():
    # Configuration
    cfg = config.Config(file("coffeesale.config"))

    # Init Qt App
    app = QtGui.QApplication(sys.argv)

    # Protocol
    protocol = ClientProtocol(cfg.client.server_url, cfg.client.server_pub, cfg.client.private_key)

    # CoffeeClient
    client = CoffeeClient()
    client.init(protocol)

    if cfg.client.hide_cursor:
        app.setOverrideCursor(QtGui.QCursor(10));

    # Init Window
    window = MainWindow(cfg)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
