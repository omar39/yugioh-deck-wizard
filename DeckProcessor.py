from PyQt5.QtCore import QThread, pyqtSignal
from CardDatabase import CardDatabse

class FinishStatus:
    SUCCESS = 0
    FAILED = 1
class DeckProcessor(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(int, str)
    def __init__(self, _card_db:CardDatabse, add_boarder:bool):
        super(DeckProcessor, self).__init__()
        self._card_db = _card_db
        self.add_boarder = add_boarder
    def _process_deck(self) :
        _target_progress = self._card_db.number_of_distinct_cards
        for _current_stats, _progress_count in self._card_db.process_deck(add_border=self.add_boarder):
            self.progress.emit(int((_progress_count / _target_progress) * 100), _current_stats)
        
    def run(self):
        try:
            self._process_deck()
            self.finished.emit(FinishStatus.SUCCESS, "Done!")
        except Exception as e:
            print(e)
            self.finished.emit(FinishStatus.FAILED, "error")
