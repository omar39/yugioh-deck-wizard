from PyQt5 import QtCore, QtGui, QtWidgets
import sys

import subprocess, platform, os

from YDKReader import Reader
from CardDatabase import CardDatabse
from gui import Ui_DeckWizard


class Inintializer:
    deckFile = None
    extraCardsZip = None
    templateFile = None
    cardBackFile = None
    window =  None
    out_folder = None

    def __init__(self, window:Ui_DeckWizard) :
        self.window = window
        self.setupCheckBoxes()
        self.setupButtons()
        self.setupLineEdit()
        self.setupComboBox()

    def getTemplateFile(self, dir=None):
        '''
        Select a file via a dialog and return the file name.
        '''
        if dir is None: dir ='./'
        fname = QtWidgets.QFileDialog.getOpenFileName(None, "Select template file...", 
                    dir, filter="(*.odg)")
        self.templateFile = fname[0]
        self.window.pushButton_selectTemplate.setText(self.templateFile.split('/')[-1])

    def getDeckFile(self, dir=None):
        '''
        Select a file via a dialog and return the file name.
        '''
        if dir is None: dir ='./'
        fname = QtWidgets.QFileDialog.getOpenFileName(None, "Select deck file...", 
                    dir, filter="All Files(*.*)")
        self.deckFile = fname[0]
        self.window.pushButton_deck.setText(self.deckFile.split('/')[-1])

    def getExtraCardsZip(self, dir=None):
        '''
        Select a file via a dialog and return the file name.
        '''
        if dir is None: dir ='./'
        fname = QtWidgets.QFileDialog.getOpenFileName(None, "Select external cards file...", 
                    dir, filter="Zip files(*.zip)")
        self.extraCardsZip = fname[0] if fname[0] != "" else None
        self.window.pushButton_external_cards.setText(self.extraCardsZip.split('/')[-1]) if self.extraCardsZip != None else None
        
    def getOutFolder(self, dir=None):
        '''
        Select a file via a dialog and return the file name.
        '''
        if dir is None: dir ='./'
        fname = QtWidgets.QFileDialog.getExistingDirectory(None, "Select output folder...")
        self.out_folder = fname
        self.window.pushButton_exportPath.setText(self.out_folder.split('/')[-1])

    def getBackSleeve(self, dir=None):
        '''
        Select a file via a dialog and return the file name.
        '''
        if dir is None: dir ='./'
        fname = QtWidgets.QFileDialog.getOpenFileName(None, "Select back sleeve file...", 
                    dir, filter="(*.jpg) ; (*.jpeg) ; (*.png)")
        self.cardBackFile = fname[0]
        self.window.pushButton_back.setText(self.cardBackFile.split('/')[-1])

    def processDeck(self):

        self.window.label_stats.setText("Processing cards..")

        card_per_page = int( self.window.lineEdit_cardPerPage.text() )
        makeBleed = self.window.checkBox_addBleed.isChecked()
        bleedVal = int(self.window.lineEdit_bleedAmt.text())
        exportPath = self.out_folder
        openFile = self.window.checkBox_openAfterFinish.isChecked()
        lang = self.window.comboBox.currentText()

        cardDB = CardDatabse(self.templateFile, 
                             self.deckFile, 
                             self.extraCardsZip,
                             self.cardBackFile, 
                             card_per_page, bleedVal, 
                             exportPath, lang)
        
        targetProgress = cardDB.number_of_distinct_cards

        for currentStats, progressCount in cardDB.process_deck(make_border=makeBleed):
            self.window.label_stats.setText(currentStats)
            self.window.progressBar.setValue( int(progressCount / targetProgress * 100) )
            
        if openFile : self.launchFile(cardDB.getDocumentFilePath())
        
    def toggleBleedOption(self):
        bleedEnabled = self.window.checkBox_addBleed.isChecked()
        self.window.lineEdit_bleedAmt.setEnabled(bleedEnabled)

    def launchFile(self, filePath:str):
        if platform.system() == 'Darwin':       
            subprocess.call(('open', filePath))
        elif platform.system() == 'Windows':        
            os.startfile(filePath)
        else:                                   
            subprocess.call(('xdg-open', filePath))
    def addLangs(self):
        languages = ['en', 'ar']
        self.window.comboBox.addItems(languages)
    def setupButtons(self):
        self.window.pushButton_selectTemplate.clicked.connect(lambda: self.getTemplateFile())
        self.window.pushButton_deck.clicked.connect(lambda : self.getDeckFile())
        self.window.pushButton_back.clicked.connect(lambda : self.getBackSleeve())
        self.window.pushButton_startMaking.clicked.connect(lambda: self.processDeck())
        self.window.pushButton_exportPath.clicked.connect(lambda: self.getOutFolder())
        self.window.pushButton_external_cards.clicked.connect(lambda: self.getExtraCardsZip())
        # self.window.pushButton_makeReceipt.clicked.connect(lambda: self.)


    def setupCheckBoxes(self):
        self.window.checkBox_addBleed.clicked.connect(lambda: self.toggleBleedOption())

    def setupLineEdit(self):
        onlyInt = QtGui.QIntValidator()
        onlyInt.setRange(1, 999)
        self.window.lineEdit_bleedAmt.setValidator(onlyInt)
        onlyInt.setRange(1, 999)
        self.window.lineEdit_cardPerPage.setValidator(onlyInt)

    def setupComboBox(self):
        self.addLangs()

    
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    DeckWizard = QtWidgets.QMainWindow()
    ui = Ui_DeckWizard()
    ui.setupUi(DeckWizard)
    init = Inintializer(ui)

    DeckWizard.show()
    sys.exit(app.exec_())