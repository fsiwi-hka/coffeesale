
class RFIDCard(object):
    mifareid = 0
    cardid = 0
    balance = 0
    used = False

    def __init__(self, mifareid = -1, cardid = -1):
        self.mifareid = mifareid
        self.cardid = cardid
        self.used = False
        self.balance = 0

    def isSame(self, other):
        if not other:
            return False

        return (other.mifareid == self.mifareid and other.cardid == self.cardid)

    def __repr__(self):
        return "<RFIDCard('%s', '%s', '%s', '%s')>" % (self.mifareid, self.cardid, self.balance, self.used)

class RFID(object):
    def __init__(self, key):

        # RFIDIOt library
        import RFIDIOtconfig

        self.key = key
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

        return RFIDCard(mifareid, cardid)

class RFIDdummy(object):
    def __init__(self, key):
        self.key = key
    
    def readCard(self):
        try:
            f = open("rfid.dummy")

            r = f.read()
            f.close()
            if r.startswith('0'):
                return None
        except:
            return None

        return RFIDCard(3, 6)