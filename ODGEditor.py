import zipfile
import xml.dom.minidom
from ZipDeck import ZipDeck

class ODGEditor:
    doc = ""
    CONTENT_XML = 'content.xml'
    NEW_DECK_ODG = '/new_deck.odg'
    IMAGE_TAG = 'draw:image'
    XLINK_HREF = 'xlink:href'
    PICS_PATH = 'Pictures/'

    def __init__(self, create_path:str, deck:dict, extra_cards:ZipDeck, card_per_page:int, template_file='Templates/9-CARD TEMPLATE.odg', back_sleeve=""):
        """
        Open an ODG file.
        """
        self.create_path = create_path
        self.template_file = template_file
        self.back_sleeve = back_sleeve
        self.deck = deck
        self.extra_cards = extra_cards
        self.card_per_page = card_per_page
        self.m_odg = zipfile.ZipFile(self.template_file)
        self.filelist = self.m_odg.infolist()
        self.content_zipinfo = ""
        for s in self.filelist:
            if s.orig_filename == self.CONTENT_XML:
                self.content_zipinfo = s
        ostr = self.m_odg.read(self.CONTENT_XML)
        self.doc = xml.dom.minidom.parseString(ostr)

    def get_out_doc(self):
        with zipfile.ZipFile(self.create_path + self.NEW_DECK_ODG) as out_doc:
            ostr = out_doc.read(self.CONTENT_XML)
            doc = xml.dom.minidom.parseString(ostr)
        return doc

    def add_pages(self, number_of_pages):
        """
        Add a number of pages with the same template.
        """
        page = self.doc.getElementsByTagName('draw:page')[0]

        for i in range (number_of_pages):
            new_page = page.cloneNode(True)
            new_page.setAttribute('draw:name', 'page' + str(i+2))
            self.doc.getElementsByTagName('office:drawing')[0].appendChild(new_page)
        print(str(number_of_pages) + " page(s) have been added.")

    def create_new_doc(self):
        try:
            with zipfile.ZipFile(self.create_path + self.NEW_DECK_ODG, 'w') as out_doc:
                for s in self.filelist:
                    try:
                        with self.m_odg.open(s) as infile:
                            if s.filename == self.CONTENT_XML:
                                out_doc.writestr(s.filename, self.doc.toxml())
                            else:
                                out_doc.writestr(s.filename, infile.read())
                    except KeyError as e:
                        print(f"Error opening file {s.filename}: {e}")
        except Exception as e:
            print(f"Failed to create new document: {e}")

    # Cleaned up the code by removing redundant 'out_doc.close()' as 'with' statement handles closing,
    # simplified string formatting using f-strings, and removed unnecessary 'try-except' blocks for 'KeyError' 
    # as 'zipfile.write()' does not raise KeyError.
    def copy_card_files(self):
        with zipfile.ZipFile(self.create_path + self.NEW_DECK_ODG, 'a') as out_doc:
            print("copying cards...")
            for card in self.deck:
                out_doc.write(f"{self.create_path}/{card}.png", f"Pictures/{card}.png")

            if self.extra_cards:
                for card in self.extra_cards.get_deck():
                    out_doc.write(f"{self.create_path}/{card}", f"Pictures/{card}")

            if self.back_sleeve:
                out_doc.write(self.back_sleeve, f"Pictures/{self.back_sleeve.split('/')[-1]}")
    
    def insert_cards(self):
        place_holders = self.doc.getElementsByTagName('draw:image')
        print(len(place_holders))
        XLINK_HREF = 'xlink:href'
        PICS_PATH = 'Pictures/'

        for card, amount in self.deck.items(): 
            for _ in range(amount):
                curr_placeholder = place_holders.item(0)
                place_holders.item(0).setAttribute(XLINK_HREF, PICS_PATH + '{}'.format(card+".png"))
                place_holders.remove(curr_placeholder)
        if self.extra_cards != None:
            for card in self.extra_cards.get_deck():
                curr_placeholder = place_holders.item(0)
                place_holders.item(0).setAttribute(XLINK_HREF, PICS_PATH + '{}'.format(card))
                place_holders.remove(curr_placeholder)

        # Add the back sleeve
        if self.back_sleeve != "":
            last_index = len(place_holders) - 1
            for i in range(self.card_per_page):
                curr_placeholder = place_holders.item(last_index-i)
                place_holders.item(last_index-i).setAttribute(XLINK_HREF, PICS_PATH + '{}'.format(self.back_sleeve.split('/')[-1]))
                place_holders.remove(curr_placeholder)
                
