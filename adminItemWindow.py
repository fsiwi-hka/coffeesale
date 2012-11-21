#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from adminItemUi import Ui_AdminItemWindow

# CoffeeClient
from coffeeclient import *

class AdminItemWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window)
        self.ui=Ui_AdminItemWindow()
        self.ui.setupUi(self)
        self.setModal(True)
        self.items = {}
        self.ui.pushApply.clicked.connect(self.pushApply)
        self.ui.pushClose.clicked.connect(self.pushClose)

    def show(self):
        QtGui.QDialog.show(self)
        self.setWindowState(QtCore.Qt.Fullscreen)

    def exec_(self):
        self.rebuildItems()
        QtGui.QDialog.exec_(self)

    def pushApply(self):
        for item in self.items:
            enabled = item.enabledCheckbox.isChecked()
            sold_out = item.soldoutCheckbox.isChecked()

            if item.enabled != enabled or item.sold_out != sold_out:
                CoffeeClient().updateItem(item.id, enabled, sold_out)
        self.accept()

    def pushClose(self):
        self.reject()

    def rebuildItems(self):
        for i in range(self.ui.itemLayout.count()): 
            self.ui.itemLayout.itemAt(i).widget().close()
        self.items = CoffeeClient().getItems()

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(50)
        font.setBold(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        
        itemPerRow = 2
        itemIndex = 0
        for item in self.items:
            label = QtGui.QLabel(self)
            label.setFont(font)
            label.setText(item.desc + "\n" + str(item.price))
            label.setSizePolicy(sizePolicy)
            label.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
            label.setStyleSheet("image: url(resource/items/" + str(item.id) + ".png);")
            self.ui.itemLayout.addWidget(label, (itemIndex / itemPerRow) * 3 + 0, itemIndex % itemPerRow)
            
            enabledCheckbox = QtGui.QCheckBox(self)
            enabledCheckbox.setText("Enabled")
            enabledCheckbox.setFont(font)
            enabledCheckbox.setChecked(item.enabled)
            self.ui.itemLayout.addWidget(enabledCheckbox, (itemIndex / itemPerRow) * 3 + 1, itemIndex % itemPerRow)
            item.enabledCheckbox = enabledCheckbox

            soldoutCheckbox = QtGui.QCheckBox(self)
            soldoutCheckbox.setText("Sold out")
            soldoutCheckbox.setFont(font)
            soldoutCheckbox.setChecked(item.sold_out)
            self.ui.itemLayout.addWidget(soldoutCheckbox, (itemIndex / itemPerRow) * 3 + 2, itemIndex % itemPerRow)
            item.soldoutCheckbox = soldoutCheckbox

            itemIndex += 1
