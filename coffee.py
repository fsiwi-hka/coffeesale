import sys, time, os
from PyQt4 import QtGui, QtCore

# Compiled ui classes
from mainUi import Ui_MainWindow
from codeUi import Ui_CodeWindow

# Constants
# Interaction timeout in seconds
INTERACTION_TIMEOUT = 7

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        # Setup signals
        self.ui.btCoffee.clicked.connect(self.pushCoffeeClicked)
        self.ui.btClubMate.clicked.connect(self.pushMateClicked)
        self.ui.btCharge.clicked.connect(self.pushChargeClicked)

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.timerUpdate)
        self.timer.start(100)

        # Code Window
        self.codeWindow = CodeWindow()

        # Business logic stuff
        self.lastInteraction = time.time()

    def timerUpdate(self):
        t = time.time()

        # Reset selection if no interaction is made after specified time
        if self.lastInteraction + INTERACTION_TIMEOUT < t:
            self.lastInteraction = t
            self.ui.btClubMate.setChecked(False)
            self.ui.btCoffee.setChecked(False)

    def pushMateClicked(self):
        self.ui.btClubMate.setChecked(True)
        self.ui.btCoffee.setChecked(False)
        
    def pushCoffeeClicked(self):
        self.ui.btClubMate.setChecked(False)
        self.ui.btCoffee.setChecked(True)

    def pushChargeClicked(self):
        self.codeWindow.show()

class CodeWindow(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.ui=Ui_CodeWindow()
        self.ui.setupUi(self)

        self.ui.pushNo1.clicked.connect(self.pushNo1)
        self.ui.pushNo2.clicked.connect(self.pushNo2)
        self.ui.pushNo3.clicked.connect(self.pushNo3)
        self.ui.pushNo4.clicked.connect(self.pushNo4)
        self.ui.pushNo5.clicked.connect(self.pushNo5)
        self.ui.pushNo6.clicked.connect(self.pushNo6)
        self.ui.pushNo7.clicked.connect(self.pushNo7)
        self.ui.pushNo8.clicked.connect(self.pushNo8)
        self.ui.pushNo9.clicked.connect(self.pushNo9)

        self.ui.pushErase.clicked.connect(self.pushErase)
        self.ui.pushConfirm.clicked.connect(self.pushConfirm)
        self.ui.pushCancel.clicked.connect(self.pushCancel)

    def pushNo(self, i):
        print i
    
    def pushErase(self):
        print "erase"

    def pushConfirm(self):
        self.close()

    def pushCancel(self):
        self.close()
    
    # Numpad logic... 
    def pushNo1(self):
        self.pushNo(1)
    def pushNo2(self):
        self.pushNo(2)
    def pushNo3(self):
        self.pushNo(3)
    def pushNo4(self):
        self.pushNo(4)
    def pushNo5(self):
        self.pushNo(5)
    def pushNo6(self):
        self.pushNo(6)
    def pushNo7(self):
        self.pushNo(7)
    def pushNo8(self):
        self.pushNo(8)
    def pushNo9(self):
        self.pushNo(9)

def main():
    app = QtGui.QApplication(sys.argv)
    window=MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
