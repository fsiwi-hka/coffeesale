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

class Wallet(object):
    id = 0
    mifareid = 0
    cardid = 0
    balance = 0

    def __init__(self, id, mifareid, cardid, balance):
        self.id = id
        self.mifareid = mifareid
        self.cardid = cardid
        self.balance = balance

class User(object):
    id = 0
    username = ""
    admin = False

    def __init__(self, id, username, admin):
        self.id = id
        self.username = username
        self.admin = admin

class Item(object):
    id = 0
    price = 0
    desc = ""
    image = ""

    def __init__(self, id, price, desc, image):
        self.id = id
        self.price = price
        self.desc = desc
        self.image = image

class CoffeeClient(object):
    protocol = None

    def __init__(self, protocol):
        self.protocol = protocol

    def request(self, action, mifareid = 0, cardid = 0, data = {}):
        try:
            req = self.protocol.buildRequest(mifareid, cardid)
            req.action = action
            req.data = data
            resp = self.protocol.sendRequest(req)
            if resp.success is False:
                return None
            return resp
        except:
            return None

    def getItems(self):
        resp = self.request("getItems")
        if resp is None:
            return None
        items = []
        for item in resp.data['items']:
            items.append(Item(item['id'], item['price'], item['desc'], item['image']))
        return items

    def getWallet(self, mifareid, cardid):
        resp = self.request("getWallet", mifareid, cardid)
        if resp is None:
            return None
        return Wallet(resp.data['wallet']['id'], resp.data['wallet']['mifareid'], resp.data['wallet']['cardid'], resp.data['wallet']['balance'])

    def getUser(self, mifareid, cardid):
        resp = self.request("getUser", mifareid, cardid)
        if resp is None:
            return None
        return User(resp.data['user']['id'], resp.data['user']['username'], resp.data['user']['admin'])

    def buyItem(self, item, mifareid, cardid):
        resp = self.request("buyItem", mifareid, cardid, {'item': item})
        if resp is None:
            return False
        return True

    def redeemToken(self, token, mifareid, cardid):
        resp = self.request("redeemToken", mifareid, cardid, {'token': token})
        if resp is None:
            return False
        return True

    def getRequest(self, url):
        return self.protocol.getRequest(url)

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

    # CoffeeClient
    client = CoffeeClient(protocol)

    if cfg.client.hide_cursor:
        app.setOverrideCursor(QtGui.QCursor(10));

    # Init Window
    window = MainWindow(rfid, client, cfg)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
