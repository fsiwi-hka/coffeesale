import sys
from PyQt4 import QtGui


# Import the compiled UI module
from coffeeUi import Ui_MainWindow

# Create a class for our main window
class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # This is always the same
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

def main():
    
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
