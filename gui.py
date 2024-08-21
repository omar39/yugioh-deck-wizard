# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'application.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DeckWizard(object):
    def setupUi(self, DeckWizard):
        DeckWizard.setObjectName("DeckWizard")
        DeckWizard.resize(702, 528)
        self.centralwidget = QtWidgets.QWidget(DeckWizard)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.checkBox_openAfterFinish = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_openAfterFinish.setObjectName("checkBox_openAfterFinish")
        self.gridLayout.addWidget(self.checkBox_openAfterFinish, 7, 1, 1, 1)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_cardPerPage = QtWidgets.QLabel(self.centralwidget)
        self.label_cardPerPage.setObjectName("label_cardPerPage")
        self.horizontalLayout_2.addWidget(self.label_cardPerPage)
        self.lineEdit_cardPerPage = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_cardPerPage.setMaxLength(3)
        self.lineEdit_cardPerPage.setObjectName("lineEdit_cardPerPage")
        self.horizontalLayout_2.addWidget(self.lineEdit_cardPerPage)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_4, 0, 2, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_pageTemplate = QtWidgets.QLabel(self.centralwidget)
        self.label_pageTemplate.setObjectName("label_pageTemplate")
        self.verticalLayout_2.addWidget(self.label_pageTemplate)
        self.label_deck = QtWidgets.QLabel(self.centralwidget)
        self.label_deck.setObjectName("label_deck")
        self.verticalLayout_2.addWidget(self.label_deck)
        self.label_back = QtWidgets.QLabel(self.centralwidget)
        self.label_back.setObjectName("label_back")
        self.verticalLayout_2.addWidget(self.label_back)
        self.label_export = QtWidgets.QLabel(self.centralwidget)
        self.label_export.setObjectName("label_export")
        self.verticalLayout_2.addWidget(self.label_export)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.pushButton_startMaking = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton_startMaking.setFont(font)
        self.pushButton_startMaking.setObjectName("pushButton_startMaking")
        self.gridLayout.addWidget(self.pushButton_startMaking, 7, 0, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_stats = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_stats.setFont(font)
        self.label_stats.setTextFormat(QtCore.Qt.RichText)
        self.label_stats.setAlignment(QtCore.Qt.AlignCenter)
        self.label_stats.setObjectName("label_stats")
        self.verticalLayout_3.addWidget(self.label_stats)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_3.addWidget(self.progressBar)
        self.gridLayout.addLayout(self.verticalLayout_3, 9, 0, 1, 3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkBox_addBleed = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_addBleed.setObjectName("checkBox_addBleed")
        self.horizontalLayout.addWidget(self.checkBox_addBleed)
        self.label_bleedAmt = QtWidgets.QLabel(self.centralwidget)
        self.label_bleedAmt.setObjectName("label_bleedAmt")
        self.horizontalLayout.addWidget(self.label_bleedAmt)
        self.gridLayout.addLayout(self.horizontalLayout, 6, 0, 1, 1)
        self.pushButton_makeReceipt = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_makeReceipt.setObjectName("pushButton_makeReceipt")
        self.gridLayout.addWidget(self.pushButton_makeReceipt, 6, 2, 1, 1)
        self.lineEdit_bleedAmt = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_bleedAmt.setEnabled(False)
        self.lineEdit_bleedAmt.setMaxLength(3)
        self.lineEdit_bleedAmt.setClearButtonEnabled(False)
        self.lineEdit_bleedAmt.setObjectName("lineEdit_bleedAmt")
        self.gridLayout.addWidget(self.lineEdit_bleedAmt, 6, 1, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_selectTemplate = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_selectTemplate.setObjectName("pushButton_selectTemplate")
        self.verticalLayout.addWidget(self.pushButton_selectTemplate)
        self.pushButton_deck = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_deck.setObjectName("pushButton_deck")
        self.verticalLayout.addWidget(self.pushButton_deck)
        self.pushButton_back = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_back.setObjectName("pushButton_back")
        self.verticalLayout.addWidget(self.pushButton_back)
        self.pushButton_exportPath = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_exportPath.setObjectName("pushButton_exportPath")
        self.verticalLayout.addWidget(self.pushButton_exportPath)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setCurrentText("")
        self.comboBox.setMinimumContentsLength(1)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout_3.addWidget(self.comboBox)
        self.gridLayout.addLayout(self.horizontalLayout_3, 5, 2, 1, 1)
        DeckWizard.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(DeckWizard)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 702, 24))
        self.menubar.setObjectName("menubar")
        DeckWizard.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(DeckWizard)
        self.statusbar.setObjectName("statusbar")
        DeckWizard.setStatusBar(self.statusbar)

        self.retranslateUi(DeckWizard)
        QtCore.QMetaObject.connectSlotsByName(DeckWizard)

    def retranslateUi(self, DeckWizard):
        _translate = QtCore.QCoreApplication.translate
        DeckWizard.setWindowTitle(_translate("DeckWizard", "Deck Wizard"))
        self.checkBox_openAfterFinish.setText(_translate("DeckWizard", "Open file after fninishing"))
        self.label_cardPerPage.setText(_translate("DeckWizard", "card per page (min 1)"))
        self.lineEdit_cardPerPage.setText(_translate("DeckWizard", "1"))
        self.label_pageTemplate.setText(_translate("DeckWizard", "Select Page Template"))
        self.label_deck.setText(_translate("DeckWizard", "Select Deck (.ydk file)"))
        self.label_back.setText(_translate("DeckWizard", "Select card back (image)"))
        self.label_export.setText(_translate("DeckWizard", "Export Path"))
        self.pushButton_startMaking.setText(_translate("DeckWizard", "Start Making!"))
        self.label_stats.setText(_translate("DeckWizard", "[stats]"))
        self.checkBox_addBleed.setText(_translate("DeckWizard", "Add bleed cutout"))
        self.label_bleedAmt.setText(_translate("DeckWizard", "Bleed amount (mm)"))
        self.pushButton_makeReceipt.setText(_translate("DeckWizard", "Make receipt"))
        self.lineEdit_bleedAmt.setText(_translate("DeckWizard", "0"))
        self.pushButton_selectTemplate.setText(_translate("DeckWizard", "Browse"))
        self.pushButton_deck.setText(_translate("DeckWizard", "Browse"))
        self.pushButton_back.setText(_translate("DeckWizard", "Browse"))
        self.pushButton_exportPath.setText(_translate("DeckWizard", "Browse"))
        self.label.setText(_translate("DeckWizard", "Select Cards Language"))
