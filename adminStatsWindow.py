#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, os
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from adminStatsUi import Ui_AdminStatsWindow

# CoffeeClient
from coffeeclient import *

class AdminStatsWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window)
        self.ui=Ui_AdminStatsWindow()
        self.ui.setupUi(self)
        self.setModal(True)

    def show(self):
        QtGui.QDialog.show(self)
        self.setWindowState(QtCore.Qt.Fullscreen)

    def exec_(self):
        self.rebuildStats()
        QtGui.QDialog.exec_(self)

    def rebuildStats(self):
        for i in range(self.ui.todayLayout.count()): 
            self.ui.todayLayout.itemAt(i).widget().close()
        for i in range(self.ui.weekLayout.count()): 
            self.ui.weekLayout.itemAt(i).widget().close()
        for i in range(self.ui.totalLayout.count()): 
            self.ui.totalLayout.itemAt(i).widget().close()
       
        items = CoffeeClient().getItems()
        stats = CoffeeClient().getStatistics()
        for item in items:
            stat = stats[str(item.id)]
            
            todayLabel = QtGui.QLabel()
            todayLabel.setText(str(stat['day_count']))
            self.ui.todayLayout.addRow(item.desc, todayLabel)

            weekLabel = QtGui.QLabel()
            weekLabel.setText(str(stat['week_count']))
            self.ui.weekLayout.addRow(item.desc, weekLabel)

            totalLabel = QtGui.QLabel()
            totalLabel.setText(str(stat['total_count']))
            self.ui.totalLayout.addRow(item.desc, totalLabel)
