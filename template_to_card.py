import os
from PIL import Image, ImageDraw, ImageFont
import requests
import io
from psd_tools import PSDImage
from card_template import CardLayout
from text_justify import TextJustification

class CardRushify:
    """A class for generating Yu-Gi-Oh! cards from templates and data."""
    def __init__(self, export_path: str):
        # --- Configuration ---
        # Define the paths and layout for your card elements.
        # These coordinates are examples and will need to be adjusted based on your actual template.
        # You can get these by opening your template image in an image editor and noting pixel positions.

        self.export_path = export_path

        # import fonts

        self.card_name_font = 'assets/fonts/Yu-Gi-Oh! Matrix Regular Small Caps 2.ttf'
        self.type_font = 'assets/fonts/stone-serif-sem-sc-itc-tt-semi.ttf'
        self.desc_font = 'assets/fonts/Yu-Gi-Oh! Matrix Book.ttf'
        self.id_font = 'assets/fonts/MatrixSmallCaps.otf'
        self.pendulum_scale_number_font = 'assets/fonts/MatrixBoldFractions.otf'
        self.normal_monster_font = 'assets/fonts/Yu-Gi-Oh! ITC Stone Serif LT Italic.ttf'
        self.atk_def_font = 'assets/fonts/Eurostile Candy W01 Semibold.ttf'

        self.text_justify_engine = TextJustification()

        # import psd file
        TEMPLATE_PSD_PATH = "assets/templates/rush_card_template.psd"
        self.template_psd = TEMPLATE_PSD_PATH
        self.psd = PSDImage.open(TEMPLATE_PSD_PATH)
        self.elements_bbox = {layer.name: layer.bbox for layer in self.psd._layers}
        self.elements_size = {layer.name: layer.size for layer in self.psd._layers}

        self.CARD_LAYOUT = {
            "id": {"position": self.elements_bbox.get("id")[:2], "font-size": 60},
            "card-artwork": {"position": self.elements_bbox.get("card-image")[:2], "size": self.elements_size.get("card-image")}, # (x, y) for top-left, (width, height)
            "card-name": {"position": self.elements_bbox.get("name")[:2], "size" :  self.elements_size.get("name"), "font-size": 215}, # (x, y) for top-left
            "card-type": {"position": self.elements_bbox.get("type")[:2], "size": self.elements_size.get("type"), "font-size": 95},
            "no-icon-type": {"position": (self.elements_bbox.get("name")[0], self.elements_bbox.get("type")[1]), "font-size": 100},
            "type/level": {"position": self.elements_bbox.get("type/level")[:2], "size": self.elements_size.get("type/level")},  # icon based on race
            "level-rank-val": {"position": self.elements_bbox.get("level-rank-val")[:2], "boundingbox": self.elements_bbox.get("level-rank-val"), "size": self.elements_size.get("level-rank-val")},
            "card-attribute": {"position": self.elements_bbox.get("attribute")[:2], "size": self.elements_size.get("attribute")}, # Position for a small attribute icon
            "card-effect": {"position": self.elements_bbox.get("desc")[:2], "size": self.elements_size.get("desc"), "font-size": 65},
            "atk/def": {"position": self.elements_bbox.get("atk/def")[:2], "boundingbox": self.elements_bbox.get("atk/def"), "size": self.elements_size.get("atk/def"), "font-size": 90},
            "atk-icon": {"position": self.elements_bbox.get("atk-icon")[:2], "size": self.elements_size.get("atk-icon")},
            "def-icon": {"position": self.elements_bbox.get("def-icon")[:2], "size": self.elements_size.get("def-icon")},
            # link layout
            "link-val": {"position": self.elements_bbox.get("link-val")[:2], "font-size": 100},
            "link-Top" : {"position": self.elements_bbox.get("link-up")[:2], "size": self.elements_size.get("link-up")},
            "link-Bottom" : {"position": self.elements_bbox.get("link-down")[:2], "size": self.elements_size.get("link-down")},
            "link-Left": {"position": self.elements_bbox.get("link-left")[:2], "size": self.elements_size.get("link-left")},
            "link-Right": {"position": self.elements_bbox.get("link-right")[:2], "size": self.elements_size.get("link-right")},
            "link-Top-Left": {"position": self.elements_bbox.get("link-up-left")[:2], "size": self.elements_size.get("link-up-left")},
            "link-Top-Right": {"position": self.elements_bbox.get("link-up-right")[:2], "size": self.elements_size.get("link-up-right")},
            "link-Bottom-Left": {"position": self.elements_bbox.get("link-down-left")[:2], "size": self.elements_size.get("link-down-left")},
            "link-Bottom-Right": {"position": self.elements_bbox.get("link-down-right")[:2], "size": self.elements_size.get("link-down-right")},
            # pendulum layout
            "pendulum": {"position": (0, 0)},
            "pendulum-holder": {"position": self.elements_bbox.get("pendulum-holder")[:2], "size": self.elements_size.get("pendulum-holder")},
            "pendulum-desc": {"position": self.elements_bbox.get("pendulum-desc")[:2], "size": self.elements_size.get("pendulum-desc"), "font-size": 75},
            "scale-left" : {"position": self.elements_bbox.get("scale-left")[:2], "size": self.elements_size.get("scale-left"), "font-size": 130},
            "scale-right" : {"position": self.elements_bbox.get("scale-right")[:2], "size": self.elements_size.get("scale-right"), "font-size": 130},
        }
    # --- Helper Functions ---
    def add_text(self, draw: ImageDraw, text, font_file, size, text_color, position):
        font = ImageFont.truetype(font_file, size=size)
        draw.text(position, text, fill=text_color, font=font)

    def shrink_text_to_fit(self, text: str, font: str, target_width: int, font_size: int, color:tuple[int, int, int], stroke_width: float=0):
        """Shrinks the text to fit within a specific width."""
        # create an new RGBA image with the size of text with the given font and size
        loaded_font = ImageFont.truetype(font, size=font_size)
        width, height = loaded_font.getbbox(text)[2:]
        text_image = Image.new(mode='RGBA', size=(width, height))

        # draw the text on the image
        text_draw = ImageDraw.Draw(text_image)
        text_draw.text((0, 0), text, font=loaded_font, fill=color, stroke_fill=color, stroke_width=stroke_width)
        if text_image.width <= target_width:
            return text_image
        #  chech the width of the text, if bigger than the target width, shrink new image width
        text_image = text_image.resize((target_width, text_image.height))
        return text_image
    def get_card_data_from_api(self, card_id):
        """
        Fetches card data from the Yu-Gi-Oh! API.
        In a real application, you'd handle API keys, rate limits, and error handling.
        """
        api_url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?id={card_id}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            data = response.json()
            if data and data.get('data'):
                card_info = data['data'][0]
                # Extract relevant info. This structure might vary slightly based on card type.
                return {
                    "name": card_info.get("name", "Unknown Card"),
                    "type": card_info.get("type", "Unknown Type"),
                    "frameType": card_info.get("frameType"),
                    "typeline": card_info.get("typeline", []),
                    "race": card_info.get("race", "Unknown Race"),
                    "attribute": card_info.get("attribute", "Unknown Attribute"),
                    "level": card_info.get("level") if card_info.get("type").lower().find("monster") != -1 else 0,
                    "scale": card_info.get("scale", -1),
                    "linkval": card_info.get("linkval", -1),
                    "linkmarkers": card_info.get("linkmarkers", []),
                    "atk": card_info.get("atk") if card_info.get("type").lower().find("monster") != -1 else 0,
                    "def": card_info.get("def") if card_info.get("type").lower().find("monster") != -1 else 0,
                    "desc": card_info.get("desc", ""),
                    "pend_desc": card_info.get("pend_desc", ""),
                    "monster_desc": card_info.get("monster_desc", ""),
                    "card_artwork": card_info.get("card_images")[0].get('image_url_cropped'),
                    "card_artwork_backup": card_info.get("card_images")[0].get('image_url')
                }
            else:
                print(f"No data found for card ID: {card_id}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for card ID {card_id}: {e}")
            return None

    def download_image(self, url) -> Image.Image:
        """Downloads an image from a URL and returns a PIL Image object."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            # check if image is 1:1 ratio
            if image.size[0] != image.size[1]:
                # crop image
                image = image.crop((0, 0, image.size[0], image.size[0]))
            return image.convert("RGB")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image from {url}: {e}")
            return None
        except IOError:
            print(f"Error opening image from {url}")
            return None
    def configure_card_artwork(self, id, card_data): 
        exception_artworks = os.listdir("assets/exception_artwork")
        if f"{id}.jpg" in exception_artworks:
            return Image.open(f"assets/exception_artwork/{id}.jpg").convert("RGB")
        card_image_url = card_data.get('card_artwork')
        card_image = self.download_image(card_image_url)
        if card_image == None:
            card_image_url = card_data.get('card_artwork_backup')
            card_image = self.download_image(card_image_url)

        if card_image.size[0] != card_image.size[1]:
            # crop image
            card_image = card_image.crop((0, 0, card_image.size[0], card_image.size[0]))

        card_image = card_image.resize(self.CARD_LAYOUT.get('card-artwork').get('size'), Image.Resampling.LANCZOS)
        return card_image        
    def parse_ydk(self, ydk_file_path):
        """
        Parses a .ydk file and returns a list of card IDs.
        This is a simplified parser; YDK can have side decks, extra decks, etc.
        """
        card_ids = []
        try:
            with open(ydk_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('!'):
                        try:
                            card_id = int(line)
                            card_ids.append(card_id)
                        except ValueError:
                            print(f"Warning: Skipping invalid line in YDK file: {line}")
            return card_ids
        except FileNotFoundError:
            print(f"Error: YDK file not found at {ydk_file_path}")
            return []
    
    def build_type_text(self, card_data):
        if card_data.get('frameType').lower().find(CardLayout.SPELL) != -1 or card_data.get('frameType').lower().find(CardLayout.TRAP) != -1:
            return f"[{card_data.get('frameType').capitalize()} Card]"
        else:
            frame_type =[CardLayout.SYNCHRO, CardLayout.RITUAL, CardLayout.LINK, CardLayout.XYZ, CardLayout.FUSION, CardLayout.TOKEN]
            type_text = card_data.get('race').capitalize() + "/" + (card_data.get('frameType').capitalize() + "/" if card_data.get('frameType') in frame_type else "")
            if card_data.get('type').lower().find('pendulum') != -1:
                type_text += "Pendulum/"
            if card_data.get('type').lower().find('union') != -1:
                type_text += "Union/"
            if card_data.get('type').lower().find('tuner') != -1:
                type_text += "Tuner/"
            if card_data.get('type').lower().find('spirit') != -1:
                type_text += "Spirit/"
            if card_data.get('type').lower().find('gemini') != -1:
                type_text += "Gemini/"
            if card_data.get('type').lower().find('union') != -1:
                type_text += "Union/"
            if card_data.get('frameType').find('effect') != -1:
                type_text += "Effect"
            else:
                type_text += "Normal"
            return f"[{type_text}]"
    def get_card_icon_race(self, card_race, card_desc=""):
        if card_race.lower().find('equip') != -1:
            card_race_icon = Image.open("assets/icons/equip.png")
        elif card_race.lower().find('quick') != -1:
            card_race_icon = Image.open("assets/icons/quick.png")

        elif card_race.lower().find('continuous') != -1:
            card_race_icon = Image.open("assets/icons/continuous.png")

        elif card_race.lower().find('ritual') != -1:
            card_race_icon = Image.open("assets/icons/ritual.png")

        elif card_race.lower().find('field') != -1:
            card_race_icon = Image.open("assets/icons/field.png")
        elif card_race.lower().find('counter') != -1:
            card_race_icon = Image.open("assets/icons/counter.png")
        elif card_desc and card_desc.lower().find('fusion summon') != -1:
            card_race_icon = Image.open("assets/icons/fusion.png")
        else:
            card_race_icon = Image.open("assets/icons/normal.png")
        return card_race_icon

    def is_link_or_zero_level(self, card_data):
        frametype = card_data.get('frameType').lower()
        level = card_data.get('level')
        if frametype.find(CardLayout.SPELL) != -1 or frametype.find(CardLayout.TRAP) != -1:
            return False
        elif frametype.find(CardLayout.LINK) != -1 or (level != None and level == 0):
            return True
        else:
            return False
    def get_level_rank(self, level, type, is_tuner):
        if level == None or level <= 0:
            return None
        elif type.lower().find(CardLayout.XYZ) != -1:
            return Image.open(f"assets/ranks/{level}.png")
        elif is_tuner:
            return Image.open(f"assets/levels/tuner/{level}.png")
        else :
            return Image.open(f"assets/levels/non-tuner/{level}.png")
    def get_star_icon(self, is_level):
        if is_level:
            return Image.open(f"assets/levels/icon.png")
        else:
            return Image.open(f"assets/ranks/icon.png")
    def get_attribute(self, attribute):
        try:
            return Image.open(f"assets/attributes/{attribute}.png")
        except FileNotFoundError:
            return None
    def set_pendulum_data(self, draw, base_image, card_data):
        pendulum_holder_pos = self.CARD_LAYOUT["pendulum-holder"]["position"]
        pendulum_holder_size = self.CARD_LAYOUT["pendulum-holder"]["size"]
        scale_left_pos = self.CARD_LAYOUT["scale-left"]["position"]
        scale_right_pos = self.CARD_LAYOUT["scale-right"]["position"]
        scale_size_1 = self.CARD_LAYOUT["scale-left"]["size"]
        scale_size_2 = self.CARD_LAYOUT["scale-right"]["size"]
        scale_number_font_size = self.CARD_LAYOUT["scale-right"]["font-size"]
        pendulum_effect = card_data.get('pend_desc')
        pendulum_effect_pos = self.CARD_LAYOUT["pendulum-desc"]["position"]
        pendulum_effect_size = self.CARD_LAYOUT["pendulum-desc"]["size"]
        pendulum_effect_font_size = self.CARD_LAYOUT["pendulum-desc"]["font-size"]

        pendulum_holder = Image.open('assets/misc/pendulum_holder.png')
        pendulum_holder = pendulum_holder.convert("RGBA")
        pendulum_holder = pendulum_holder.resize(pendulum_holder_size, Image.Resampling.LANCZOS)
        base_image.paste(pendulum_holder, pendulum_holder_pos, pendulum_holder)

        # 5.3 Add the pendulum scale values
        scale_val = str(card_data.get('scale'))

        # draw.text(scale_left_pos, scale_val, fill=(0, 0, 0), font=ImageFont.truetype(self.pendulum_scale_number_font, size=scale_number_font_size))
        # draw.text(scale_right_pos, scale_val, fill=(0, 0, 0), font=ImageFont.truetype(self.pendulum_scale_number_font, size=scale_number_font_size))
        scale_size = scale_size_1
        if int(scale_val) > 9:
            scale_size = scale_size_2
            scale_left_pos = (scale_left_pos[0] - 22, scale_left_pos[1]) # half digit size
            scale_right_pos = (scale_right_pos[0] - 22, scale_right_pos[1])
        scale_left_image = self.shrink_text_to_fit(scale_val, self.pendulum_scale_number_font, scale_size[0], scale_number_font_size, (0, 0, 0), 1.3)
        scale_right_image = self.shrink_text_to_fit(scale_val, self.pendulum_scale_number_font, scale_size[0], scale_number_font_size, (0, 0, 0), 1.3)

        base_image.paste(scale_left_image, scale_left_pos, scale_left_image)
        base_image.paste(scale_right_image, scale_right_pos, scale_right_image)

        # 5.4 Add pendulum effect

        best_font_size, pendulum_effect = self.text_justify_engine.justify_yugioh_text(pendulum_effect, pendulum_effect_font_size, pendulum_effect_size[0], pendulum_effect_size[1], self.desc_font)
        
        draw.text(pendulum_effect_pos, pendulum_effect, fill=(0, 0, 0), font=ImageFont.truetype(self.desc_font, size=best_font_size))
    def place_link_markers(self, base_image, link_markers: list):
        for marker in link_markers:
            position = self.CARD_LAYOUT[f"link-{marker}"]["position"] 
            size = self.CARD_LAYOUT[f"link-{marker}"]["size"] 
            link_marker = Image.open(f"assets/linkmarkers/{marker}.png")
            link_marker = link_marker.resize(size, Image.Resampling.LANCZOS)
            base_image.paste(link_marker, position, link_marker)

    def generate_card(self, id):
        """
        Generates a single Yu-Gi-Oh! card image.
        """
        special_cards = {
            "10000020": "slifer",
            "10000000": "obelisk",
            "10000010": "ra",
            "6007213": "slifer",
            "32491822": "ra",
            "69890967": "obelisk"         
        }
        card_data = self.get_card_data_from_api(id)
        card_type = CardLayout().get_card_layout(card_data.get('frameType'))
        base_image = None
        try:    
            if special_cards.get(str(id)) is not None:
                base_image = Image.open(f'assets/templates/{special_cards[str(id)]}.jpg').convert("RGB")
            else:
                base_image = Image.open(f'assets/templates/{card_type["label"]}.jpg').convert("RGB")
        except FileNotFoundError:
            print(f"Error: Template image not found at templates/{card_type}")
            return
        except Exception as e:
            print(f"Error opening template image: {e}")
            return

        draw = ImageDraw.Draw(base_image)

        #### Starting with the main layouts #####

        # 1. Place Pendulum frame, and placeholder if pendulum
        if card_data.get('frameType').lower().find(CardLayout.PENDULUM) != -1:
            pendulum_frame_pos = self.CARD_LAYOUT["pendulum"]["position"]
            pendulum_frame = Image.open(f"assets/templates/{CardLayout.PENDULUM}.png")
            pendulum_frame = pendulum_frame.convert("RGBA")
            base_image.paste(pendulum_frame, pendulum_frame_pos, pendulum_frame)
       
        # 2. Place Card Name
        name_pos = self.CARD_LAYOUT["card-name"]["position"]
        name_size = self.CARD_LAYOUT["card-name"]["size"]
        name_font_size = self.CARD_LAYOUT["card-name"]["font-size"]

        name_text = self.shrink_text_to_fit(card_data.get('name'), self.card_name_font, name_size[0], name_font_size, card_type["name"]["color"], 1.75)

        base_image.paste(name_text, name_pos, name_text)

        # change color set of the card if pendulum after adding name
        if card_data.get("frameType").lower().find(CardLayout.PENDULUM) != -1:
            card_type = CardLayout().get_card_layout(CardLayout.PENDULUM)

        # 2. Place Card Artwork
        card_artwork = self.configure_card_artwork(id, card_data)
        card_artwork_pos = self.CARD_LAYOUT["card-artwork"]["position"]
        card_artwork_size = self.CARD_LAYOUT["card-artwork"]["size"]
        card_artwork = card_artwork.resize(card_artwork_size, Image.Resampling.LANCZOS)
        base_image.paste(card_artwork, card_artwork_pos)
        # 4 Add the pendulum data if pendulum
        if card_data.get('frameType').lower().find(CardLayout.PENDULUM) != -1:
            self.set_pendulum_data(draw, base_image, card_data)
        
        # 3. Place card type
        type_pos = self.CARD_LAYOUT["card-type"]["position"] if not self.is_link_or_zero_level(card_data) else self.CARD_LAYOUT["no-icon-type"]["position"]
        type_size = self.CARD_LAYOUT["card-type"]["size"]
        type_font_size = self.CARD_LAYOUT["card-type"]["font-size"]
        type_text = '/'.join(card_data.get('typeline')) if len(card_data.get('typeline')) > 0 else card_data.get('type')
        type_text = f"[{type_text}]"

        if card_data.get("frameType").lower() == CardLayout.TOKEN:
            type_text = self.build_type_text(card_data)

        type_text_image = self.shrink_text_to_fit(type_text, self.type_font, type_size[0], type_font_size, card_type["type"]["color"], 1.5)
        base_image.paste(type_text_image, type_pos, type_text_image)

        # 5. Place Card ID
        id_pos = self.CARD_LAYOUT["id"]["position"]
        id_font_size = self.CARD_LAYOUT["id"]["font-size"]
        id_stats = str(id)
        if card_data.get("frameType").lower() == CardLayout.TOKEN:
            id_stats = "Non Deck card"
        draw.text(id_pos, id_stats, fill=card_type.get('id').get('color'), font=ImageFont.truetype(self.id_font, size=id_font_size))

        # 6. Place card effect
        card_desc = card_data.get('monster_desc')
        card_desc = card_data.get('desc') if card_desc == "" else card_desc

        effect_pos = self.CARD_LAYOUT["card-effect"]["position"]
        effect_size = self.CARD_LAYOUT["card-effect"]["size"]
        effect_font_size = self.CARD_LAYOUT["card-effect"]["font-size"]
        font_type = self.desc_font if card_data.get("frameType").lower().find(CardLayout.NORMAL) == -1 else self.normal_monster_font

        best_font_size, card_desc = self.text_justify_engine.justify_yugioh_text(card_desc, effect_font_size, effect_size[0], effect_size[1], font_type)
        draw.text(effect_pos, card_desc, fill=(0, 0, 0), font=ImageFont.truetype(font_type, size=best_font_size))

        # 8. Place card icon
        type_level_pos = self.CARD_LAYOUT['type/level']['position']
        type_level_size = self.CARD_LAYOUT['type/level']['size']
        card_icon = None
        card_frame = card_data.get('frameType')
        if card_frame == CardLayout.SPELL or card_frame == CardLayout.TRAP:
            icon_image = self.get_card_icon_race(card_data.get('race'), card_data.get('desc'))
            card_icon = icon_image
        elif card_frame == CardLayout.LINK:
            pass
        if card_icon:
            card_icon = card_icon.resize(type_level_size, Image.Resampling.LANCZOS)
            base_image.paste(card_icon, type_level_pos, card_icon)

        # 9. Place monster attribute
        if card_frame != CardLayout.SPELL and card_frame != CardLayout.TRAP:
            attribute = card_data.get('attribute').lower()
            attribute_pos = self.CARD_LAYOUT["card-attribute"]["position"]
            attribute_size = self.CARD_LAYOUT["card-attribute"]["size"]

            attribute_icon = self.get_attribute(attribute)
            if attribute_icon:
                attribute_icon.resize(attribute_size, Image.Resampling.LANCZOS)
                base_image.paste(attribute_icon, attribute_pos, attribute_icon)

            level = card_data.get('level')
            if card_frame != CardLayout.LINK and level != None and level > 0:
                # 10. Place monster leve/rank
                level_pos = self.CARD_LAYOUT["type/level"]["position"]
                level_size = self.CARD_LAYOUT["type/level"]["size"]
                

                level_rank_icon = self.get_star_icon(card_data.get('frameType').lower().find(CardLayout.XYZ) == -1)
                level_rank_icon = level_rank_icon.resize(level_size, Image.Resampling.LANCZOS)

                level_val_size = self.CARD_LAYOUT["level-rank-val"]["size"]
                level_val_bb = self.CARD_LAYOUT["level-rank-val"]["boundingbox"]
                level_val_image = self.get_level_rank(level, card_data.get('frameType'), card_data.get('type').lower().find('tuner') != -1)

                base_image.paste(level_rank_icon, level_pos, level_rank_icon)

                if level == 1:
                    level_val_size = (int(level_val_size[0] * 0.6), level_val_size[1])
                    # fix bounding box based on size. shift the position to right
                    level_val_bb = (int(level_val_bb[0] * 0.6) + int(level_val_bb[0] / 1.7), level_val_bb[1], int(level_val_bb[2] * 0.6) + int(level_val_bb[0] / 1.7), level_val_bb[3])
                level_val_image = level_val_image.resize(level_val_size, Image.Resampling.LANCZOS)

               
                base_image.paste(level_val_image, level_val_bb, level_val_image)

            # 11. Place ATK, DEF
            # 11.1 Set icons
            atk_icon_pos = self.CARD_LAYOUT["atk-icon"]["position"]
            atk_icon_size = self.CARD_LAYOUT["atk-icon"]["size"]
            def_icon_pos = self.CARD_LAYOUT["def-icon"]["position"]
            def_icon_size = self.CARD_LAYOUT["def-icon"]["size"]

            atk_icon = Image.open("assets/misc/atk_icon.png")
            atk_icon = atk_icon.resize(atk_icon_size, Image.Resampling.LANCZOS)
            base_image.paste(atk_icon, atk_icon_pos, atk_icon)

            def_icon = Image.open("assets/misc/def_icon.png")
            def_icon = def_icon.resize(def_icon_size, Image.Resampling.LANCZOS)

            if card_data.get("frameType").lower().find(CardLayout.LINK) == -1:
                base_image.paste(def_icon, def_icon_pos, def_icon)

            # 11.2 Add atk/def values
            atk_def_font_size = self.CARD_LAYOUT["atk/def"]["font-size"]
            atk_def_size = self.CARD_LAYOUT["atk/def"]["size"]
            atk_def_concat = None
            if card_data.get("frameType").lower().find(CardLayout.LINK) == -1:
                atk_def_concat = f"{card_data.get('atk') if card_data.get('atk') != -1 else '?'} | {card_data.get('def') if card_data.get('def') != -1 else '?'}" 
            else:
                atk_def_concat = f"{card_data.get('atk')} | LINK-{card_data.get('linkval')}"
            atk_def_image = self.shrink_text_to_fit(atk_def_concat, self.atk_def_font, atk_def_size[0], atk_def_font_size, (0, 0, 0), 1.5)
            # make the atk_def_image right in the center between atk_icon and def_icon
            atk_def_position = (int((atk_icon_pos[0] + def_icon_pos[0] + atk_icon_size[0] - atk_def_image.width) / 2), self.CARD_LAYOUT["atk/def"]["position"][1])
            base_image.paste(atk_def_image, atk_def_position, atk_def_image)
            # 12. Place link markers if LINK
            if card_data.get("frameType").lower().find(CardLayout.LINK) != -1:
                self.place_link_markers(base_image, card_data.get("linkmarkers"))
        
        if card_data:
                output_filename = os.path.join(self.export_path, f"{id}.jpg")
                base_image.save(output_filename)
                return True
        else:
            print(f"Skipping card ID {id} due to data fetching issues.")
            return False
# write a test trial for a single card

if __name__ == "__main__":
    card_rushify = CardRushify("./Images Database/rush")
    card_id = '57116034'
    card_rushify.generate_card(card_id)