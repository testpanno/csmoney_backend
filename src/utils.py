from fastapi import HTTPException
import json

def debug_mode(fn):
    def wrapped():
        try:
            return fn()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return wrapped

def get_latest_price(item_data):
    if 'prices' in item_data and 'latest' in item_data['prices']:
        return item_data['prices']['latest']
    else:
        return None

async def get_log_total_price(log):
    prices = {}

    with open('prices_ext.json', 'r', encoding='utf-8') as f:
        prices = json.load(f)

    skins = [item['market_hash_name'] for item in log['items_from_them']]

    total_log_value = 0

    for skin in skins:
        for item_data in prices["data"]:
            if item_data.get('market_hash_name') == skin:
                latest_price = get_latest_price(item_data)
                if latest_price is not None:
                    total_log_value += latest_price
                break

    return str(round(total_log_value, 2))
