import json
import os
from decimal import Decimal

import requests
from dotenv import load_dotenv

load_dotenv()

WEI_TO_ETH_SCALE = Decimal(10**18)
TOKEN_CACHE_DIR = "token_cache"
TOKEN_TRAIT_TYPES = ["SUITON", "DOTON", "KINTON", "KATON", "MOKUTON"]


def get_listed_token_id_to_price(api_key, contract_address):
    url = "https://api.opensea.io/v2/listings/collection/very-long-cnp/all?limit=100"

    response = requests.get(
        url,
        headers={
            "accept": "application/json",
            "X-API-KEY": api_key,
        },
    )
    response.raise_for_status()

    token_id_to_price = {}
    token_id_to_end_time = {}
    for listing in response.json()["listings"]:
        token_id = listing["protocol_data"]["parameters"]["offer"][0][
            "identifierOrCriteria"
        ]
        price = int(listing["price"]["current"]["value"])
        endtime = int(listing["protocol_data"]["parameters"]["endTime"])
        if token_id in token_id_to_price:
            if token_id_to_end_time[token_id] > endtime:
                continue
        token_id_to_price[token_id] = price
        token_id_to_end_time[token_id] = endtime

    return token_id_to_price


def get_traits(token_id, token_json_url):
    os.makedirs(TOKEN_CACHE_DIR, exist_ok=True)
    cache_file = f"{TOKEN_CACHE_DIR}/{token_id}.json"
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)

    url = f"{token_json_url}{token_id}.json"
    response = requests.get(
        url,
        headers={
            "accept": "application/json",
        },
    )
    response.raise_for_status()

    traits = list(
        filter(
            lambda x: x["trait_type"] in TOKEN_TRAIT_TYPES,
            response.json()["attributes"],
        )
    )

    with open(cache_file, "w") as f:
        json.dump(traits, f)

    return traits


def get_token_id_to_total_level(token_ids, token_json_url):
    token_id_to_total_level = {}
    for token_id in token_ids:
        total_level = 0
        traits = get_traits(token_id, token_json_url)
        for trait in traits:
            total_level += int(trait["value"])
        token_id_to_total_level[token_id] = total_level
    return token_id_to_total_level


def get_eth_price(price):
    wei = Decimal(price)
    eth = wei / WEI_TO_ETH_SCALE
    return eth

# フロアプライスの昇順にCSVに出力
def output_csv(token_id_to_price, token_id_to_total_level, contract_address):
    with open("token_id_to_price_and_total_level.csv", "w") as f:
        f.write("token_id,price,total_level,url\n")
        for token_id, price in sorted(token_id_to_price.items(), key=lambda x: x[1]):
            f.write(
                f"{token_id},{get_eth_price(price)},{token_id_to_total_level[token_id]},https://opensea.io/assets/ethereum/{contract_address}/{token_id}\n"
            )


def main():
    api_key = os.getenv("API_KEY")
    contract_address = os.getenv("CONTRACT_ADDRESS")
    token_json_url = os.getenv("TOKEN_JSON_URL")

    token_id_to_price = get_listed_token_id_to_price(api_key, contract_address)
    token_id_to_total_level = get_token_id_to_total_level(
        token_id_to_price.keys(), token_json_url
    )
    output_csv(token_id_to_price, token_id_to_total_level, contract_address)


if __name__ == "__main__":
    main()
