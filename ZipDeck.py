import zipfile
class ZipDeck:
    deck = list()
    def __init__(self, file_name:str, working_dir:str):
        # unzip file
        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(working_dir)
            # get list of files
            for file in zip_ref.infolist():
                if file.filename.__contains__("jpg") \
                    or file.filename.__contains__("jpeg") \
                    or file.filename.__contains__("png") \
                    or file.filename.__contains__("jfif") \
                    or file.filename.__contains__("JPG") \
                    or file.filename.__contains__("JPEG") \
                    or file.filename.__contains__("PNG") \
                    or file.filename.__contains__("JFIF"):
                    self.deck.append(file.filename)
    def get_deck(self):
        return self.deck