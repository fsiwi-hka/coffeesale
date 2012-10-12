import string
import base64
import struct
import time
from array import array
from PyQt4.QtCore import *

def toUInt16BE(data, off):
    s = chr(data[off]) + chr(data[off+1])
    return struct.unpack(">H", s)[0]

def toUInt16LE(data, off):
    s = chr(data[off]) + chr(data[off+1])
    return struct.unpack("<H", s)[0]

class RFIDCard(object):
    mifareid = 0
    cardid = 0
    valid = False
    balance = 0
    ccBalance = -1
    ccLastBalance = -1

    def __init__(self, mifareid = -1, cardid = -1):
        self.mifareid = mifareid
        self.cardid = cardid
        self.valid = False
        self.balance = 0
        self.ccBalance = -1
        self.ccLastBalance = -1

    def isSame(self, other):
        if not other:
            return False

        return (other.mifareid == self.mifareid and other.cardid == self.cardid)

    def __repr__(self):
        return "<RFIDCard('%s', '%s', '%s', '%s')>" % (self.mifareid, self.cardid, self.valid, self.balance)

class RFIDWorkerBase(QThread):
    key = ""
    def __init__(self, key, parent=None):
        self.key = key
        QThread.__init__(self, parent)

    def __del__(self):
        None

    def run(self):
        None

class RFIDWorker(RFIDWorkerBase):
    def __init__(self, key, parent=None):
        RFIDWorkerBase.__init__(self, key, parent)
        self.key = key

        # RFIDIOt library
        global RFIDIOtconfig
        import RFIDIOtconfig

    def run(self):
        while True:
            card = self.readCard()
            self.emit(SIGNAL("cardRead(PyQt_PyObject)"), card)
            time.sleep(0.25)
    
    def readBlock(self, block, key):
        self.card.select()
        if self.card.login(block/4, 'AA', key):
            self.card.readMIFAREblock(block)
            return self.card.MIFAREdata
        return None

    def parseWallet(self):
        block24 = self.readBlock(24, 'A0A1A2A3A4A5')
        block25 = self.readBlock(25, 'A0A1A2A3A4A5')
        block26 = self.readBlock(26, 'A0A1A2A3A4A5')
        data = bytearray(base64.b16decode(block24 + block25 + block26))

        key = int(data[41])
        for i in range(9, 45):
            data[i] = data[i] ^ key

        WALLET_TCOUNT_KEY = 0x0404
        value_key = toUInt16BE(data, 42)
        front_value = toUInt16LE(data, 26) ^ value_key
        back_value = toUInt16LE(data, 31) ^ value_key ^ 0x3b05
        front_count = toUInt16BE(data, 28) ^ WALLET_TCOUNT_KEY
        back_count = toUInt16BE(data, 33) ^ WALLET_TCOUNT_KEY ^ 0x3d3e

        if front_count == back_count:
            currentBalance = float(front_value) / 100.0
            lastBalance = float(back_value) / 100.0
        else:
            currentBalance = float(back_value) / 100.0
            lastBalance = float(front_value) / 100.0

        return [currentBalance, lastBalance]

    def readCard(self):
        if self.card is None:
            try:
                global RFIDIOtconfig
                RFIDIOtconfig  = reload(RFIDIOtconfig)

                self.card = RFIDIOtconfig.card
            except Exception as e:
                return None

        try:
            if not self.card.select():
                return None
        except:
            self.card.ser.close()
            self.card = None
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
            self.card.ser.close()
            self.card = None
            return None

        if cardid == -1 or mifareid == -1:
            return None
        
        wallet = [-1, -1]
        try:
            wallet = self.parseWallet()
        except:
            pass

        card = RFIDCard(mifareid, cardid)
        card.ccBalance = wallet[0]
        card.ccLastBalance = wallet[1]
        return card

class RFIDDummyWorker(RFIDWorkerBase):
    def __init__(self, key, parent=None):
        RFIDWorkerBase.__init__(self, key, parent)

    def run(self):
        while True:
            card = self.readCard()
            self.emit(SIGNAL("cardRead(PyQt_PyObject)"), card)
            time.sleep(0.25)

    def readCard(self):
        card = "0"
        try:
            f = open("rfid.dummy")

            r = f.read()
            f.close()
            i = r[0:1]
            if i == "0":
                return None
            else:
                card = i
        except:
            return None

        if card == "0":
            return None
    
        if card == "1":
            return RFIDCard(3, 6)

        if card == "2":
            return RFIDCard(4, 7)

        if card == "3":
            return RFIDCard(5, 8)

        return RFIDCard(3, 6)
