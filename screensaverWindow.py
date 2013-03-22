#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os, random, KAMensa, datetime
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from screensaverUi import Ui_Screensaver

class ScreensaverWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui=Ui_Screensaver()
        self.ui.setupUi(self)

        self.shuffleTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.shuffleTimer, QtCore.SIGNAL("timeout()"), self.shuffle)
        self.shuffleTimer.start(5000)

        self.updateTimer = QtCore.QTimer()
        QtCore.QObject.connect(self.updateTimer, QtCore.SIGNAL("timeout()"), self.updateMensa)
        self.updateTimer.start(60000)

        self.setModal(True)
        self.ui.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.updateMensa()

    def show(self):
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setModal(True)
        self.updateMensa()
        self.ui.frame.resize(self.ui.frame.sizeHint())
        QtGui.QDialog.show(self)

        # EVIL HACK FOR XMONAD/X11/XORG
        desk = QtGui.QDesktopWidget()
        r = desk.screenGeometry()
        offset = 4
        self.setGeometry(r.left()-offset, r.top()-offset, r.width()+offset*2, r.height()+offset*2)

        if not self.isVisible():
            self.shuffle()

    def updateMensa(self):
               
        # On weekends, print plan for monday
        date = datetime.date.today();
        if date.weekday() == 5 :
            date += datetime.timedelta(2)
        elif date.weekday() == 6:
            date += datetime.timedelta(1)

        plan = KAMensa.mensaplan()
        header = KAMensa.key_to_name('moltke') + " " + str(date)
        mensa = header + "\n"

        for line in plan.keys('moltke'):
            meal = plan.meal('moltke',line,date)
            if meal != None :
                    # Linie
                    linie = ""
                    for item in meal:
                        if 'nodata' not in item.keys():
                            linie += ''+ item['meal'] + ' ' + item['dish'] + ' ' + str(item['price_1']) + u'€ ' + item['info']
                            linie += ' '
                    if linie != "":
                        mensa += '\n' + str(KAMensa.key_to_name(line)) + ':\n' + linie 
        self.ui.mensaLabel.setText(mensa)

    def shuffle(self):
        offset = 25
        self.ui.frame.setGeometry(random.randint(0-offset, self.width() - self.ui.frame.width()+offset), random.randint(0-offset, self.height() - self.ui.frame.height()+offset), self.ui.frame.width(), self.ui.frame.height()) 

    def mousePressEvent(self, event):
        #button = event.button()
        self.close()

    def keyPressEvent(self, event):            
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        return
