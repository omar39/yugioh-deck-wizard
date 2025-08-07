import pandas as pd
import requests
import os
from io import BytesIO
from SuperResolution import SuperResolution
import numpy as np
from PIL import Image
import time
import numpy as np
import math
from YDKReader import Reader
from ODGEditor import ODGEditor
from ZipDeck import ZipDeck
import csv
from logger import Logger
from template_to_card import CardRushify
import cv2

class CardDatabse:
    api = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    database_filename = "database.csv"
    database_folder = "./Images Database/"
    ENGLISH = 'en'
    ARABIC = 'ar'
    ANIME = 'anime'
    RUSH = 'rush'
    database = pd.DataFrame()
    logger = Logger()

    number_of_distinct_cards = None
    current_number_count = 1
    def __init__(self, template_file:str, deck_file:str, extra_file:str, back_sleeve:str, card_per_page:int, bleed_val:int, out_folder:str, format:str):
        self.database = self.import_database()
        self.template_file = template_file
        self.deck_file = deck_file
        self.extra_file = extra_file
        self.back_sleeve = back_sleeve
        self.out_folder = out_folder
        self.card_per_page = card_per_page
        self.bleed_val = bleed_val
        self.format = format

        self.deck = Reader(self.deck_file)

        if self.extra_file != None :
            self.extra_cards = None
            self.extra_cards = ZipDeck(self.extra_file, self.out_folder)
        else :
           self.extra_cards = None

        self.number_of_distinct_cards = len(self.deck.get_result()) + len(self.extra_cards.get_deck()) if self.extra_cards != None else len(self.deck.get_result())

        self.rushifier = CardRushify(os.path.join(self.database_folder, self.RUSH))

    def import_database(self):
        '''
        Import database. A dataframe object is then returned
        '''
        try :
            database = pd.read_csv(self.database_filename, index_col="id")
            database.index = database.index.astype(str)
            return database
        except FileNotFoundError:
            self.logger.info("Database file not found. Creating it now...")
            # create the database csv file
            database = self.create_database_file()           
            self.update_database()
            return self.import_database()
    
    def create_database_file(self):
        # create new csv file with database name
        with open(self.database_filename, 'w', newline='') as csvfile:
            fieldnames = ['id', 'name', 'image_url', 'image_url_en', 'upscaled_image']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
        return pd.read_csv(self.database_filename, index_col="id")

    def update_database(self):
        """Update cards database for newer cards."""
        url = self.api
        database_filename = self.database_filename
        try:
            response = requests.get(url, timeout=60)
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f'connection error: {e}. Please check your internet connection')
            return
        if response.status_code == 200:
            data = response.json()
            df = pd.json_normalize(data['data'], record_path=['card_images'], meta=['name', 'frameType', 'type'])
            df = df.iloc[1:]
            df['upscaled_image'] = ""
            df = df.set_index('id')
            df.index = df.index.astype(str)
            df = df.rename(columns={"image_url": "image_url_en"})
            df["image_url_ar"] = [f"https://www.arab-duelists.com/assets/img/cards/{i}.jpg" for i in df.index]
            for lang in ["en", "ar"]:
                saved_images = os.listdir(f"./Images Database/{lang}/")
                for i in saved_images:
                    if i.endswith(".jpg"):
                        df.at[i.split(".jpg")[0], f"upscaled_image_{lang}"] = f"./Images Database/{lang}/" + i
            df.to_csv(database_filename)
            self.database = df
    def get_image(self, id, lang):
        response_success = False
        image_lang = 'image_url_{}'.format(lang)
        image_url = self.database.at[id, image_lang]
        while response_success == False:
            try:
                image = requests.get(image_url, timeout=60)
                response_success = image.status_code == 200
                if image.status_code == 404:
                    return self.process_card(id, self.ENGLISH)
            except requests.exceptions.ConnectionError:
                self.logger.error('connection error!\ntrying in 30 seconds..')
                time.sleep(30)            
        if response_success == True: 
            self.logger.info("image retrieved!")
        image = Image.open(BytesIO(image.content))
        return image
    
    def upscale_image_local(self, image_path:str):
        '''
        Upscale a given image url using RDN Super Resolution neural network. The image file path is then returned.
        '''    
        sr = SuperResolution()
        sr.upscale_image(image_path, image_path)
    
    def process_card(self, id:str, format:str):
        '''
        Start processing a card given its id. The image file is then returned.
        '''
        upscale_format = 'upscaled_image_{}'.format(format)
        image_path = ""
        if format == self.ANIME:
            if id + ".jpg" in os.listdir(self.database_folder + "/" + format):
                image_path = self.database_folder + self.format + "/" + id + ".jpg"
                image = Image.open(open(image_path, 'rb'))

                if image.size[0] * image.size[1] < 3e5:
                    self.logger.info("Image is not upscaled, upscaling...")
                    self.upscale_image_local(image_path)
            else:
                self.logger.info("Anime card image not found.\nProccessing english version...")
                return self.process_card(id, self.ENGLISH)
        elif format == self.RUSH:
            if f"{id}.jpg" in os.listdir(self.database_folder + "/" + format):
                image_path = self.database_folder + self.format + "/" + id + ".jpg"
            else:
                self.logger.info(f"{format} card image not found.")
                is_generated = self.rushifier.generate_card(id)
                if is_generated:
                    image_path = self.database_folder + self.format + "/" + id + ".jpg"
                else:
                    return self.process_card(id, self.ENGLISH)
        else:
            if id + ".jpg" not in os.listdir(self.database_folder + "/" + format):
                self.logger.info(self.database.at[id, 'name'])
                self.logger.info(f"Card of id {id} not found.\nProccessing now...")

                image_path = self.database_folder + self.format + '/' + id + '.jpg'
                image = self.get_image(id, format)
                
                if image.size[0] * image.size[1] < 5e5:
                    self.upscale_image_local(image_path)
                image = image.convert('RGB')
                image.save(image_path, 'JPEG')
                
                self.database.at[id, upscale_format] = image_path
                self.database.to_csv("./" + self.database_filename)
            else:
                #get the image directly
                image_path = self.database_folder + self.format + '/' + id + '.jpg'
                self.logger.info("Image found at " + image_path)

        return Image.open(image_path)
    
    def add_border(self, image:Image, border_size_mm:float):
        if border_size_mm == 0:
            return image
        width, height = image.size
        mm_to_pixel = width / 66
        border_size = math.ceil(mm_to_pixel * border_size_mm)
        half_pixel = math.floor(mm_to_pixel / 2)
        border = cv2.copyMakeBorder(
            np.array(image),
            top=border_size - half_pixel,
            bottom=border_size - half_pixel,
            left=border_size + half_pixel,
            right=border_size + half_pixel,
            borderType=cv2.BORDER_REPLICATE,
            value=[200, 200, 200]
        )
        return Image.fromarray(border)
    
    def save_image(self, image:Image, folder_name:str, image_count:int, file_name:str):
        for i in range(1, image_count+1):
            image = image.convert('RGB')
            image.save(folder_name + '/' + "{} ({}).jpg".format(file_name, i), "JPEG")

    def process_deck(self, add_border: bool = False):
        self.logger.info(f"*****************Processing Deck at {self.deck_file}***********************")
        distinct_card_count = len(self.deck.get_result())
        missing_cards = []
        for card_id, _ in self.deck.get_result().items():
            card_id_str = str(card_id)
            if self.format != self.ANIME:
                if card_id_str not in self.database.index:
                    self.logger.info(f"Card with id {card_id_str} not found in database\nUpdating database...")
                    self.update_database()
                    if card_id_str not in self.database.index:
                        self.logger.error(f"Card with id {card_id_str} not found in database")
                        yield (f"Card with id {card_id_str} not found in database", self.current_number_count)
                        missing_cards.append(card_id_str)
                        continue
                card_name = self.database.at[card_id_str, 'name']
                yield (f"Processing \"{card_name}\"", self.current_number_count)
            else:
                yield (f"Processing \"{card_id_str} - Anime Card\"", self.current_number_count)

            image = self.process_card(card_id_str, self.format)

            if add_border:
                image = self.add_border(image, border_size_mm=self.bleed_val)

            self.logger.info(f'[{self.current_number_count} card of {distinct_card_count} distinct cards]')

            self.current_number_count += 1
            image = image.convert('RGB')
            image.save(f"{self.out_folder}/{card_id_str}.jpg", "JPEG")

        if self.extra_cards:
            self.proccess_extra_cards(add_border=add_border)

        # remove the missing cards
        for card_id in missing_cards:
            del self.deck.get_result()[card_id]

        yield ("Creating File..", 100)
        self.create_doc_file()

        # remove cards from folder
        self.remove_cards_images()

        yield ("Deck Done!", 0)
        self.logger.info("****************Deck Done!******************")
        # log process stats
        self.logger.info(f"Cards Processed: {self.current_number_count}")
        self.logger.info(f"Missing Cards Count: {len(missing_cards)}")
        self.logger.info(f"Missing Cards: {missing_cards}")
    
    def proccess_extra_cards(self, add_border: bool):
        for file_name in self.extra_cards.get_deck():
                image_path = f"{self.out_folder}/{file_name}"
                image = Image.open(image_path)
                if add_border:
                    image = self.add_border(image, border_size_mm=self.bleed_val)
                    image = image.convert('RGB')
                    image.save(image_path, "JPEG")

    def remove_cards_images(self):
        files = os.listdir(self.out_folder)
        for file in files:
            if file.endswith(".jpg"):
                os.remove(self.out_folder + "/" + file)

    def get_document_file_path(self):
        return self.out_folder + "/new_deck.odg"

    def create_doc_file(self):
        '''
        Create a .odg file placing the file in 'folder_name', 
        adding cards in 'deck' and placing the desired sleeve (optional)
        '''
        
        back = self.add_border(Image.open(self.back_sleeve), self.bleed_val) 
        back_path = self.out_folder + "/back.jpg"
        back = back.convert('RGB')
        back.save(back_path, "JPEG")
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
