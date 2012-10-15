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
        self.rebuildItems()
        self.ui.pushApply.clicked.connect(self.pushApply)
        self.ui.pushClose.clicked.connect(self.pushClose)

    def show(self):
        QtGui.QDialog.show(self)
        self.setWindowState(QtCore.Qt.Fullscreen)

    def exec_(self):
        QtGui.QDialog.exec_(self)
        self.rebuildItems()

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
        font.setPointSize(12)
        font.setWeight(75)
        font.setBold(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        for item in self.items:
            label = QtGui.QLabel(self)
            label.setFont(font)
            label.setText(item.desc + "\n" + str(item.price))
            label.setSizePolicy(sizePolicy)
            label.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
            label.setStyleSheet("image: url(resource/items/" + str(item.id) + ".png);")
            self.ui.itemLayout.addWidget(label, 0, item.id)
            
            enabledCheckbox = QtGui.QCheckBox(self)
            enabledCheckbox.setText("Enabled")
            enabledCheckbox.setChecked(item.enabled)
            self.ui.itemLayout.addWidget(enabledCheckbox, 1, item.id)
            item.enabledCheckbox = enabledCheckbox

            soldoutCheckbox = QtGui.QCheckBox(self)
            soldoutCheckbox.setText("Sold out")
            soldoutCheckbox.setChecked(item.sold_out)
            self.ui.itemLayout.addWidget(soldoutCheckbox, 2, item.id)
            item.soldoutCheckbox = soldoutCheckbox
