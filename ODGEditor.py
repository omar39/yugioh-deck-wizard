import os, sys
import zipfile
import xml.dom.minidom
from YDKReader import Reader

class ODGEditor:
    doc = ""
    def __init__(self, create_path:str, deck:dict, template_file='Templates/OgTemplate.odg', back_sleev=""):
        """
        Open an ODG file.
        """
        self.create_path = create_path
        self.template_file = template_file
        self.back_sleev = back_sleev
        self.deck = deck
        self.m_odg = zipfile.ZipFile(self.template_file)
        self.filelist = self.m_odg.infolist()
        self.content_zipinfo = ""
        for s in self.filelist:
            if s.orig_filename == 'content.xml':
                self.content_zipinfo = s
        ostr = self.m_odg.read('content.xml')
        self.doc = xml.dom.minidom.parseString(ostr)

    def get_out_doc(self):
        """
        
        """
        with zipfile.ZipFile(self.create_path + '/new_deck.odg') as out_doc:
            ostr = out_doc.read('content.xml')
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
        with zipfile.ZipFile(self.create_path + '/new_deck.odg', 'w') as out_doc:
            for s in self.filelist:
                with self.m_odg.open(s) as infile:
                    if s.filename == 'content.xml':
                        out_doc.writestr(s.filename, self.doc.toxml())
                    else:
                        out_doc.writestr(s.filename, infile.read())
            out_doc.close()

    def copy_card_files(self):
        with zipfile.ZipFile(self.create_path + '/new_deck.odg', 'a') as out_doc:
            print("copying cards...")
            for card in self.deck.keys():
                out_doc.write("./{}/{}".format('Images Database', card+".png"), "{}/{}".format("Pictures", card+".png"))
            if not self.back_sleev == "": out_doc.write(self.back_sleev, "{}/{}".format("Pictures", self.back_sleev.split('/')[-1]))
            out_doc.close()
    
    def insert_cards(self):
        #doc = self.get_out_doc()add_cards
        place_holders = self.doc.getElementsByTagName('draw:image')
        print(len(place_holders))
        for card, amount in self.deck.items(): 
            for _ in range(amount):
                curr_placeholder = place_holders.item(0)
                place_holders.item(0).setAttribute('xlink:href', 'Pictures/{}'.format(card+".png"))
                place_holders.remove(curr_placeholder)
        if not self.back_sleev == "":
            last_index = len(place_holders) - 1
            for i in range(9):
                curr_placeholder = place_holders.item(last_index-i)
                place_holders.item(last_index-i).setAttribute('xlink:href', 'Pictures/{}'.format(self.back_sleev.split('/')[-1]))
                place_holders.remove(curr_placeholder)
                
# deck = Reader('YDK Files/Cyberse strucutre deck.ydk')
# odg = ODGEditor('Templates/OgTemplate.odg', deck.get_result())

# odg.add_pages(6)
# odg.add_cards()
