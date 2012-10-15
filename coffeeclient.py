#!/usr/bin/python
# -*- coding: utf-8 -*-

# Protocol
from coffeeprotocol import *

# HTTPS Request
import httpsclient

# Message window
from messageWindow import *

class Singleton(object):
    def __new__(type, *args):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

    def __init__(self):
        if not '_ready' in dir(self):
            self._ready = True

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
    enabled = True
    sold_out = False

    def __init__(self, id, price, desc, image, enabled, sold_out):
        self.id = id
        self.price = price
        self.desc = desc
        self.image = image
        self.enabled = enabled
        self.sold_out = sold_out

class CoffeeClient(Singleton):
    protocol = None
    mifareid = -1
    cardid = -1

    def init(self, protocol):
        self.protocol = protocol

    def setIds(self, mifareid, cardid):
        self.mifareid = mifareid
        self.cardid = cardid

    def resetIds(self):
        self.setIds(0, 0)

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
            items.append(Item(item['id'], item['price'], item['desc'], item['image'], item['enabled'], item['sold_out']))
        return items

    def getWallet(self):
        resp = self.request("getWallet", self.mifareid, self.cardid)
        if resp is None:
            return None
        return Wallet(resp.data['wallet']['id'], resp.data['wallet']['mifareid'], resp.data['wallet']['cardid'], resp.data['wallet']['balance'])

    def getUser(self):
        resp = self.request("getUser", self.mifareid, self.cardid)
        if resp is None:
            return None
        return User(resp.data['user']['id'], resp.data['user']['username'], resp.data['user']['admin'])

    def updateItem(self, itemid, enabled, sold_out):
        resp = self.request("updateItem", self.mifareid, self.cardid, {'item': itemid, 'enabled': enabled, 'sold_out': sold_out})
        if resp is None:
            return False
        return True

    def buyItem(self, item):
        resp = self.request("buyItem", self.mifareid, self.cardid, {'item': item})
        if resp is None:
            return False
        return True

    def redeemToken(self, token):
        resp = self.request("redeemToken", self.mifareid, self.cardid, {'token': token})
        if resp is None:
            return False
        return True
    def getStatistics(self):
        resp = self.request("getStatistics", self.mifareid, self.cardid)
        if resp is None:
            return None
        return resp.data['statistics']

    def getRequest(self, url):
        return self.protocol.getRequest(url)
