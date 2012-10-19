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
      
        columns = {'day': self.ui.todayLayout, 'week': self.ui.weekLayout, 'total': self.ui.totalLayout}
        
        for key, layout in columns.items():
            revenue = 0
            for item in items:   
                revenue += stats[key]['items'][str(item.id)]['revenue']
                label = QtGui.QLabel()
                label.setText(str(stats[key]['items'][str(item.id)]['count']))
                layout.addRow(item.desc + ":", label)

            rlabel = QtGui.QLabel()
            rlabel.setText(str(revenue))
            layout.addRow("Revenue:", rlabel)
 
            tlabel = QtGui.QLabel()
            tlabel.setText(str(stats[key]['used_tokens']))
            layout.addRow("Redeemed tokens:", tlabel)
            tvlabel = QtGui.QLabel()
            tvlabel.setText(str(stats[key]['used_tokens_value']))
            layout.addRow("Token value:", tvlabel)
        

