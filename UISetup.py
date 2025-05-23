from PyQt5 import QtGui, QtWidgets

import subprocess, platform, os

from CardDatabase import CardDatabse
from ReceiptGenerator import YugiohReceipt
from DeckProcessor import FinishStatus, DeckProcessor
from gui import Ui_DeckWizard

class UISetup:
    _deck_file = None
    _extra_cards_zip = None
    _template_file = None
    _card_back_file = None
    _out_folder = None
    

    def __init__(self, window:Ui_DeckWizard) :
        self._window = window
        self._deck_processor = None
        self._setup_check_boxes()
        self._setup_buttons()
        self._setup_line_edit()
        self._setup_combo_box()

    def _get_template_file(self, selected_dir=None):
        '''
        Select a file via a dialog and return the file name.
        '''
        if selected_dir is None: selected_dir = './'
        fname = QtWidgets.QFileDialog.getOpenFileName(None, "Select template file...", 
                    selected_dir, filter="(*.odg)")
        self._template_file = fname[0]
        self._window.pushButton_selectTemplate.setText(self._template_file.split('/')[-1])

    def _get_deck_file(self, selected_dir=None):
        '''
        Select a file via a dialog and return the file name.
        '''
        if selected_dir is None: selected_dir ='./'
        fname = QtWidgets.QFileDialog.getOpenFileName(None, "Select deck file...", 
                    selected_dir, filter="All Files(*.*)")
        self._deck_file = fname[0]
        self._window.pushButton_deck.setText(self._deck_file.split('/')[-1])

    def _get_extra_cards_zip(self, selected_dir=None):
        '''
        Select a file via a dialog and return the file name.
        '''
        if selected_dir is None: selected_dir ='./'
        fname = QtWidgets.QFileDialog.getOpenFileName(None, "Select external cards file...", 
                    selected_dir, filter="Zip files(*.zip)")
        self._extra_cards_zip = fname[0] if fname[0] != "" else None
        self._window.pushButton_external_cards.setText(self._extra_cards_zip.split('/')[-1]) if self._extra_cards_zip != None else None
        
    def _get_out_folder(self):
        '''
        Select a file via a dialog and return the file name.
        '''
        fname = QtWidgets.QFileDialog.getExistingDirectory(None, "Select output folder...")
        self._out_folder = fname
        self._window.pushButton_exportPath.setText(self._out_folder.split('/')[-1])

    def _get_back_sleeve(self, selected_dir=None):
        '''
        Select a file via a dialog and return the file name.
        '''
        if selected_dir is None: selected_dir ='./'
        fname = QtWidgets.QFileDialog.getOpenFileName(None, "Select back sleeve file...", 
                    selected_dir, filter="(*.jpg) ; (*.jpeg) ; (*.png)")
        self._card_back_file = fname[0]
        self._window.pushButton_back.setText(self._card_back_file.split('/')[-1])

    def _check_for_inputs(self):
        if (self._deck_file != None or self._extra_cards_zip != None) \
            and self._template_file != None and self._card_back_file != None and self._out_folder != None :
            return True
        return False
    def _prepare_deck(self):

        if not self._check_for_inputs():
            return

        self._display_message("Processing cards..")

        _card_per_page = int( self._window.lineEdit_cardPerPage.text() )
        _make_bleed = self._window.checkBox_addBleed.isChecked()
        _bleed_val = int(self._window.lineEdit_bleedAmt.text())
        _export_path = self._out_folder
        _lang = self._window.comboBox.currentText()

        _card_db = CardDatabse(self._template_file, 
                             self._deck_file, 
                             self._extra_cards_zip,
                             self._card_back_file, 
                             _card_per_page, _bleed_val, 
                             _export_path, _lang)
        self._deck_processor = DeckProcessor(_card_db, _make_bleed)
        self._deck_processor.progress.connect(lambda progress, stats: self._yield_deck_progress(stats, progress))
        self._deck_processor.finished.connect(lambda status_code, message: self._deck_process_finished(status_code, _card_db.get_document_file_path()))
        self._deck_processor.start()

    def _deck_process_finished(self, status_code:int, deck_file:str):
        self._deck_processor.terminate()
        self._deck_processor = None
        if status_code == FinishStatus.FAILED:
            self._display_message("Failed to process deck")
        else :
            self._display_message("Successfully processed deck")
            _open_file = self._window.checkBox_openAfterFinish.isChecked()
            if _open_file : self._launch_file(deck_file)
    def _yield_deck_progress(self, stats: str, progress:int):
        self._display_message(stats)
        self._window.progressBar.setValue(progress)

    def _toggle_bleed_option(self):
        _bleed_enabled = self._window.checkBox_addBleed.isChecked()
        self._window.lineEdit_bleedAmt.setEnabled(_bleed_enabled)

    def _launch_file(self, file_path:str):
        if platform.system() == 'Darwin':       
            subprocess.call(('open', file_path))
        elif platform.system() == 'Windows':        
            os.startfile(file_path)
        else:                                   
            subprocess.call(('xdg-open', file_path))
    def _add_langs(self):
        languages = ['en', 'ar', 'anime']
        self._window.comboBox.addItems(languages)
    def _make_receipt(self):
        if not self._check_for_inputs():
            return
        receipt = YugiohReceipt(self._deck_file, self._extra_cards_zip, 1.5, 2, self._out_folder)
        output_file = receipt.generate_receipt()
        self._launch_file(output_file)
    def _setup_buttons(self):
        self._window.pushButton_selectTemplate.clicked.connect(lambda: self._get_template_file())
        self._window.pushButton_deck.clicked.connect(lambda : self._get_deck_file())
        self._window.pushButton_back.clicked.connect(lambda : self._get_back_sleeve())
        self._window.pushButton_startMaking.clicked.connect(lambda: self._prepare_deck())
        self._window.pushButton_exportPath.clicked.connect(lambda: self._get_out_folder())
        self._window.pushButton_external_cards.clicked.connect(lambda: self._get_extra_cards_zip())
        self._window.pushButton_makeReceipt.clicked.connect(lambda: self._make_receipt())


    def _setup_check_boxes(self):
        self._window.checkBox_addBleed.clicked.connect(lambda: self._toggle_bleed_option())

    def _setup_line_edit(self):
        only_int = QtGui.QIntValidator()
        only_int.setRange(1, 999)
        self._window.lineEdit_bleedAmt.setValidator(only_int)
        only_int.setRange(1, 999)
        self._window.lineEdit_cardPerPage.setValidator(only_int)

    def _setup_combo_box(self):
        self._add_langs()
        
    def _display_message(self, message:str):
        self._window.label_stats.setText(message)
