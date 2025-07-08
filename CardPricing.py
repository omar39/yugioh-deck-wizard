import pandas as pd
import numpy as np
import math
class CardPricing:
    NORMAL = 'Normal'
    CUSTOM = 'Custom'
    def __init__(self):
        try:
            self.prices = pd.read_csv('Prices.csv')
        except FileNotFoundError:
            self.prices = self.__create_pricing_table()
            self.prices.to_csv('Prices.csv')
    def __create_pricing_table(self) -> pd.DataFrame:
        data = {'Type': ['Normal', 'Normal', 'Normal', 'Normal','Normal', 'Custom', 'Custom', 'Custom'],
                'Min': [1, 101, 201, 501, 1001, 1, 101, 201],
                'Max': [100, 200, 500, 1000, np.inf, 100, 200, np.inf],
                'Price': [2, 1.75, 1.65, 1.5, 1.35, 2.5, 2, 1.75]}
        prices = pd.DataFrame(data)
        return prices
    def get_price_range(self, card_type, cards_number) -> float:
        columns = ['Min', 'Max', 'Price']
        try:
            target_class = self.prices.groupby('Type') \
                .get_group(card_type) \
                .sort_values(ascending=True, by='Min')[columns]            
            for min, max , price in target_class.iloc:
                if cards_number > min and cards_number <= max:
                    return math.floor(price * cards_number)
            return 0.0
        except Exception:
            print("An error occured")