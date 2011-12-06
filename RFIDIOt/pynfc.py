#!/usr/bin/python

from ctypes import *
import binascii
import logging
import time
import readline
import RFIDIOtconfig

DCO_HANDLE_CRC              = 0x00
DCO_HANDLE_PARITY           = 0x01
DCO_ACTIVATE_FIELD          = 0x10
DCO_INFINITE_LIST_PASSIVE   = 0x20
DCO_INFINITE_SELECT         = 0x20
DCO_ACCEPT_INVALID_FRAMES   = 0x30
DCO_ACCEPT_MULTIPLE_FRAMES  = 0x31

IM_ISO14443A_106  = 0x00
IM_FELICA_212     = 0x01
IM_FELICA_424     = 0x02
IM_ISO14443B_106  = 0x03
IM_JEWEL_106      = 0x04

MAX_FRAME_LEN = 264




class TAG_INFO_ISO14443A(Structure):
	_fields_ = [('abtAtqa', c_ubyte * 2),
				('btSak', c_ubyte),
				('uiUidLen', c_ulong),
				('abtUid', c_ubyte * 10),
				('uiAtsLen', c_ulong),
				('abtAts', c_ubyte * 36)]
				

class ISO14443A(object):
	def __init__(self, ti):
		self.uid = "".join(["%02x" % x for x in ti.abtUid[:ti.uiUidLen]])
		if ti.uiAtsLen:
			self.atr = "".join(["%02x" % x for x in ti.abtAts[:ti.uiAtsLen]])
		else:
			self.atr = ""
	
	def __str__(self):
		rv = "ISO14443A(uid='%s', atr='%s')" % (self.uid, self.atr)
		return rv
		

class NFC(object):

	def __init__(self):
		self.LIB = "/usr/local/lib/libnfc.so"
		#self.LIB = "/usr/local/lib/libnfc_26102009.so.0.0.0"
		#self.LIB = "./libnfc_nvd.so.0.0.0"
		#self.LIB = "./libnfc_26102009.so.0.0.0"		
		self.device = None
		self.poweredUp = False

		if RFIDIOtconfig.debug:
			self.initLog()
		self.initlibnfc()
		self.configure()
	
	def __del__(self):
		self.deconfigure()

	def initLog(self, level=logging.DEBUG):
#	def initLog(self, level=logging.INFO):
		self.log = logging.getLogger("pynfc")
		self.log.setLevel(level)
		sh = logging.StreamHandler()
		sh.setLevel(level)
		f = logging.Formatter("%(asctime)s: %(levelname)s - %(message)s")
		sh.setFormatter(f)
		self.log.addHandler(sh)

	def initlibnfc(self):
		if RFIDIOtconfig.debug:
			self.log.debug("Loading %s" % self.LIB)
		self.libnfc = CDLL(self.LIB)

	def configure(self):
		if RFIDIOtconfig.debug:
			self.log.debug("Connecting to NFC reader")
		#self.device = self.libnfc.nfc_connect()
		self.device = self.libnfc.nfc_connect(None)
		if RFIDIOtconfig.debug:
			if self.device == None:
				self.log.error("Error opening NFC reader")
			else:
				self.log.debug("Opened NFC reader")	
			self.log.debug("Initing NFC reader")	
		#self.libnfc.nfc_reader_init(self.device)
		self.libnfc.nfc_initiator_init(self.device)		
		if RFIDIOtconfig.debug:
			self.log.debug("Configuring NFC reader")

  		# Drop the field for a while
		self.libnfc.nfc_configure(self.device,DCO_ACTIVATE_FIELD,False);
  	
  		# Let the reader only try once to find a tag
  		self.libnfc.nfc_configure(self.device,DCO_INFINITE_SELECT,False);
		#self.libnfc.nfc_configure(self.device,DCO_INFINITE_LIST,false);
  		self.libnfc.nfc_configure(self.device,DCO_HANDLE_CRC,True);
		self.libnfc.nfc_configure(self.device,DCO_HANDLE_PARITY,True);
		self.libnfc.nfc_configure(self.device,DCO_ACCEPT_INVALID_FRAMES, True);
  		# Enable field so more power consuming cards can power themselves up
  		self.libnfc.nfc_configure(self.device,DCO_ACTIVATE_FIELD,True);
		
	def deconfigure(self):
		if self.device != None:
			if RFIDIOtconfig.debug:
				self.log.debug("Deconfiguring NFC reader")
			#self.powerOff()
			self.libnfc.nfc_disconnect(self.device)
			if RFIDIOtconfig.debug:
				self.log.debug("Disconnected NFC reader")
			self.device == None
	
	def powerOn(self):
		self.libnfc.nfc_configure(self.device, DCO_ACTIVATE_FIELD, True)
		if RFIDIOtconfig.debug:
			self.log.debug("Powered up field")
		self.poweredUp = True
	
	def powerOff(self):
		self.libnfc.nfc_configure(self.device, DCO_ACTIVATE_FIELD, False)
		if RFIDIOtconfig.debug:
			self.log.debug("Powered down field")
		self.poweredUp = False
	
	def readISO14443A(self):
		"""Detect and read an ISO14443A card, returns an ISO14443A() object."""

		self.log.debug("Polling for ISO14443A cards")
		ti = TAG_INFO_ISO14443A()
		r = self.libnfc.nfc_initiator_select_tag(self.device, IM_ISO14443A_106, None, None, byref(ti))
		self.log.debug('card Select r: ' + str(r))
		if r == None or r ==0:
			self.log.error("No cards found, trying again")
			time.sleep(1)
			result = self.readISO14443A()
			return result
		else:
			self.log.debug("Card found")
			return ISO14443A(ti)

	def sendAPDU(self, apdu):
		txData = []		
		for i in range(0, len(apdu), 2):
			txData.append(int(apdu[i:i+2], 16))
	
		txAPDU = c_ubyte * len(txData)
		tx = txAPDU(*txData)

		rxAPDU = c_ubyte * MAX_FRAME_LEN
		rx = rxAPDU()
		rxlen = c_ulong()

	
		if RFIDIOtconfig.debug:	
			self.log.debug("Sending %d byte APDU: %s" % (len(tx),"".join(["%02x" % x for x in tx])))
#			self.log.debug("Sending %d byte APDU: %s" % (len(tx)-1,"".join(["%02x" % x for x in tx[1:]])))		
		#r = self.libnfc.nfc_initiator_transceive_bytes(self.device, byref(tx), c_ulong(len(tx)), byref(rx), byref(rxlen))
		r = self.libnfc.nfc_initiator_transceive_dep_bytes(self.device, byref(tx), c_ulong(len(tx)), byref(rx), byref(rxlen))		
		if RFIDIOtconfig.debug:
			self.log.debug('APDU r =' + str(r))
		if r == 0:
			if RFIDIOtconfig.debug:
				self.log.error("Error sending/recieving APDU, cycling power and trying again")
			time.sleep(1)
			result = self.sendAPDU(apdu)
			return result
		else:
			rxAPDU = "".join(["%02x" % x for x in rx[:rxlen.value]])
			if RFIDIOtconfig.debug:
				self.log.debug("Recieved %d byte APDU: %s" % (rxlen.value, rxAPDU))
			return rxAPDU

if __name__ == "__main__":
	n = NFC()
	n.powerOn()
	c = n.readISO14443A()
	print 'UID: ' + c.uid
	print 'ATR: ' + c.atr

	cont = True
	while cont:
		apdu = raw_input("enter the apdu to send now:")
		if apdu == 'exit':
			cont = False
		else:
			r = n.sendAPDU(apdu)
			print r

	print 'Ending now ...'
	n.deconfigure()
