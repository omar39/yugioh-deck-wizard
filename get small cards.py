# download all small cards in database

import pandas as pd
import requests
import os

database_filename = "database.csv"
database = pd.read_csv(database_filename, index_col="id")
database.index = database.index.astype(str)

for card_id in database.index:
    card_image = database.at[card_id, "image_url_small"]
    frameType = database.at[card_id, "frameType"]
    card_name = "".join(c for c in database.at[card_id, "name"] if c.isalnum() or c in (' ', '_', '-')).strip()
    if os.path.exists(f"small cards/{frameType}/{card_name}/{card_id}.jpg"):
        print(f"Skipping {card_id}, already downloaded")
        continue
    if frameType in ["skill", "token"]: continue
    print(f"Downloading {card_id}, {card_image}")
    if not os.path.exists(f"small cards/{frameType}/{card_name}"):
        os.makedirs(f"small cards/{frameType}/{card_name}")

    for i in range(5):
        try:
            response = requests.get(card_image, timeout=10)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {card_id}, trial {i+1}: {e}")
            if i == 4:
                print(f"failed downloading {card_id}, skipping")
                continue

    with open(f"small cards/{frameType}/{card_name}/{card_id}.jpg", "wb") as f:
        f.write(response.content)
    print(f"Finished downloading {card_id}")
