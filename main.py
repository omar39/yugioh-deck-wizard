import sys
from PyQt5 import QtWidgets

from UISetup import UISetup
from gui import Ui_DeckWizard

    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    DeckWizard = QtWidgets.QMainWindow()
    ui = Ui_DeckWizard()
    ui.setupUi(DeckWizard)
    init = UISetup(ui)

    DeckWizard.show()
    sys.exit(app.exec_())