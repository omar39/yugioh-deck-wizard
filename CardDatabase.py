import pandas as pd
import requests
import os
from io import BytesIO
from ISR.models import RDN;
import numpy as np
from PIL import Image
import time
import numpy as np
import math
from YDKReader import Reader
from ODGEditor import ODGEditor
from ZipDeck import ZipDeck

class CardDatabse:
    api = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    database_filename = "database.csv"
    database_folder = "./Images Database/"
    database = pd.DataFrame()

    number_of_distinct_cards = None
    current_number_count = 1
    def __init__(self, template_file:str, deck_file:str, extra_file:str, back_sleeve:str, card_per_page:int, bleed_val:int, out_folder:str, language:str):
        self.database = self.import_database()
        self.template_file = template_file
        self.deck_file = deck_file
        self.extra_file = extra_file
        self.back_sleeve = back_sleeve
        self.out_folder = out_folder
        self.card_per_page = card_per_page
        self.bleed_val = bleed_val
        self.language = language

        self.deck = Reader(self.deck_file)

        if self.extra_file != None :
            self.extra_cards = None
            self.extra_cards = ZipDeck(self.extra_file, self.out_folder)
        else :
           self.extra_cards = None

        self.number_of_distinct_cards = len(self.deck.get_result()) + len(self.extra_cards.get_deck()) if self.extra_cards != None else len(self.deck.get_result())

    def import_database(self):
        '''
        Import database. A dataframe object is then returned
        '''
        database = pd.read_csv(self.database_filename, index_col="id")
        database.index = database.index.astype(str)
        return database
    
    def update_database(self):
        '''
        Update cards database for newer cards.
        '''
        print("Updating Database....")
        response = requests.get(self.api)
        if response.status_code == 200:
            print("Success")
            card = response.json()
            df = pd.json_normalize(card['data'], record_path=['card_images'], meta=['name'])
            df = df[1:]
            df['upscaled_image'] = " "
            df = df.set_index('id')
            df.index = df.index.astype(str)
            df.rename(columns={"image_url" : "image_url_en"}, inplace=True)
            ar_urls = ["https://www.arab-duelists.com/assets/img/cards/{}.jpg".format(i) for i in df.index ]
            df['image_url_ar'] = ar_urls
            saved_images_en = os.listdir('./Images Database/en/')
            for i in saved_images_en:
                df.at[i.split('.png')[0], 'upscaled_image_en'] = './Images Database/en/' + i
                df.at[i.split('.png')[0], 'upscaled_image_ar'] = './Images Database/ar/' + i
            df.to_csv('./' + self.database_filename)
            return df
    def get_image(self, id, lang):
        response_success = False
        image_lang = 'image_url_{}'.format(lang)
        image_url = self.database.at[id, image_lang]
        while response_success == False:
            try:
                image = requests.get(image_url, timeout=60)
                response_success = image.status_code == 200
                if image.status_code == 404:
                    return self.process_card(id, 'en')
            except requests.exceptions.ConnectionError:
                print('connection error!\ntrying in 30 seconds..')
                time.sleep(30)            
        if response_success == True: print("image retrieved!")
        image = Image.open(BytesIO(image.content))
        return image
    
    def upscale_image_local(self, image:Image):
        '''
        Upscale a given image url using RDN Super Resolution neural network. The image file path is then returned.
        '''    
        lr_img = np.array(image)
        rdn = RDN(weights='noise-cancel')
        sr_image = rdn.predict(lr_img, by_patch_of_size=50);
        result = Image.fromarray(sr_image)
        
        return result
    
    def process_card(self, id:str, lang:str):
        '''
        Start processing a card given its id. The image file is then returned.
        '''
        upscale_lang = 'upscaled_image_{}'.format(lang)
        # see if a variable is a string and a path
        print(self.database.at[id, upscale_lang])
        proccessed = id + ".png" in os.listdir(self.database_folder + self.language)

        image_path = ""
        if proccessed == False:
            print(self.database.at[id, 'name'])
            print("Image not found.\nProccessing now...")

            image_path = self.database_folder + self.language + '/' + id + '.png'
            image = self.get_image(id, lang)
            
            if image.size[0] * image.size[1] < 9e5:
                image = self.upscale_image_local(image)
            image.save(image_path, 'PNG')
            
            self.database.at[id, upscale_lang] = image_path
            self.database.to_csv("./" + self.database_filename)
        else:
            #get the image directly
            image_path = str(self.database.at[id, upscale_lang])
            print("Image found at " + image_path)

        return Image.open(image_path)
    
    def add_border(self, image:Image, border_size_mm=int):
        import cv2
        im = np.array(image)
        mm_to_pixel = 3.7795275591
        border_size = math.ceil(mm_to_pixel * border_size_mm)
        border = cv2.copyMakeBorder(
            im,
            top=border_size,
            bottom=border_size,
            left=border_size,
            right=border_size,
            borderType=cv2.BORDER_REPLICATE,
            value=[200, 200, 200]
        )
        return Image.fromarray(border)
    
    def save_image(self, image:Image, folder_name:str, image_count:int, file_name:str):
        for i in range(1, image_count+1):
            image.save(folder_name + '/' + "{} ({}).png".format(file_name, i), "PNG")

    def process_deck(self, make_border:bool=False):
        self.number_of_distinct_cards = len(self.deck.get_result())

        for i, j in self.deck.get_result().items():
            card_id = str(i)
            if card_id not in self.database.index: self.database = self.update_database()
            image_lang = "image_url_{}".format(self.language)
            card_name = self.database.at[card_id, 'name']
            card_image = self.database.at[card_id, image_lang]
            print({card_name : card_image})
            yield ("Processing \" {} \"".format(card_name), self.current_number_count)

            
            image = self.process_card(card_id, self.language)
            
            if make_border == True : image = self.add_border(image, border_size_mm=self.bleed_val)

            print('[{} card of {} distinct cards]'.format(
                self.current_number_count, self.number_of_distinct_cards)
                )
            
            self.current_number_count += 1
            image.save(self.out_folder + '/' + "{}.png".format(card_id), "PNG")

        if(self.extra_cards != None):
            for file_name in self.extra_cards.get_deck():
                image_path = self.out_folder + '/' + file_name
                image = Image.open(image_path)
                if make_border == True : image = self.add_border(image, border_size_mm=self.bleed_val)



        yield ("Creating File..", 100)
        self.create_doc_file()

        yield("Deck Done!", 0)
        
    def get_document_file_path(self):
        return self.out_folder + "/new_deck.odg"

    def create_doc_file(self):
        '''
        Create a .odg file placing the file in 'folder_name', 
        adding cards in 'deck' and placing the desired sleeve (optional)
        '''
        back = self.add_border(Image.open(self.back_sleeve), self.bleed_val)
        back_path = self.out_folder + "/back.png"
        back.save(back_path, "PNG")
        odg_editor = ODGEditor(create_path=self.out_folder,
                              card_per_page=self.card_per_page,
                              deck=self.deck.get_result(),
                              extra_cards=self.extra_cards,
                              back_sleeve=back_path,
                              template_file=self.template_file)

        page_number = math.ceil( sum ( self.deck.get_result().values() ) + (len(self.extra_cards.get_deck()) if self.extra_cards is not None else 0)  / self.card_per_page )
        odg_editor.add_pages(page_number)
        odg_editor.insert_cards()
        odg_editor.create_new_doc()
        odg_editor.copy_card_files()