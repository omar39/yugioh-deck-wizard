from logger import Logger
class CardLayout:
    SPELL = 'spell'
    TRAP = 'trap'
    TOKEN = 'token'
    NORMAL = 'normal'
    EFFECT = 'effect'
    FUSION = 'fusion'
    SYNCHRO = 'synchro'
    RITUAL = 'ritual'
    LINK = 'link'
    XYZ = 'xyz'
    TOKEN = 'token'
    PENDULUM = 'pendulum'
    def __init__(self):
        self.logger = Logger()
        pass
    
    def get_card_layout(self, card_type):
        label = card_type.split("_")[0]
        self.logger.info(f"Card type: {label}")
        if card_type.find(CardLayout.LINK) != -1 or card_type.find(CardLayout.XYZ) != -1:
            return {
                "label": label,
                "name": {"color": (255, 255, 255)},
                "type": {"color": (255, 255, 255)},
                "id": {"color": (255, 255, 255)},
            }
        else:
            return {
                "label": label,
                "name": {"color": (0, 0, 0)},
                "type": {"color": (0, 0, 0)},
                "id": {"color": (0, 0, 0)},
            }

