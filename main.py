import json
import os
from decimal import Decimal

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ["API_KEY"]
CONTRACT_ADDRESS = os.environ["CONTRACT_ADDRESS"]
TOKEN_JSON_URL = os.environ["TOKEN_JSON_URL"]


def get_listed_token_id_to_price():
    """リストされたtoken_idとその価格の辞書を取得する"""
    url = "https://api.opensea.io/v2/listings/collection/very-long-cnp/all?limit=100"

    response = requests.get(
        url,
        headers={
            "accept": "application/json",
            "X-API-KEY": API_KEY,
        },
    )

    token_id_to_price = {}
    token_id_to_end_time = {}
    for listing in response.json()["listings"]:
        # token_idとその価格を取得
        token_id = listing["protocol_data"]["parameters"]["offer"][0][
            "identifierOrCriteria"
        ]
        price = int(listing["price"]["current"]["value"])
        endtime = int(listing["protocol_data"]["parameters"]["endTime"])
        # token_idがすでに登録されている場合は、endtimeが最新のものを採用する
        if token_id in token_id_to_price:
            if token_id_to_end_time[token_id] > endtime:
                continue
        token_id_to_price[token_id] = price
        token_id_to_end_time[token_id] = endtime

    return token_id_to_price


def get_token_id_to_total_level(token_ids):
    """token_idのリストから、そのtoken_idのtraitsを取得する"""
    token_id_to_total_level = {}
    for token_id in token_ids:
        total_level = 0
        cache_traits = []
        for trait in get_traits(token_id):
            total_level += int(trait["value"])
            cache_traits.append(trait)
        token_id_to_total_level[token_id] = total_level
        save_trait_cache_file(token_id, cache_traits)
    return token_id_to_total_level


def get_traits(token_id):
    """token_idのtraitsを取得する"""
    # token_cacheフォルダが無ければ作成
    if not os.path.exists("token_cache"):
        os.mkdir("token_cache")
    # すでにキャッシュされたものがあればそちらを取得
    if os.path.exists(f"token_cache/{token_id}.json"):
        with open(f"token_cache/{token_id}.json", "r") as f:
            return json.load(f)
    # キャッシュされていない場合はトークンのJSONファイルから取得
    url = f"{TOKEN_JSON_URL}{token_id}.json"
    response = requests.get(
        url,
        headers={
            "accept": "application/json",
        },
    )
    return list(
        filter(
            lambda x: x["trait_type"]
            in ["SUITON", "DOTON", "KINTON", "KATON", "MOKUTON"],
            response.json()["attributes"],
        )
    )


def save_trait_cache_file(token_id, trait: dict):
    """token_cache/{token_id}.jsonにtraitsを保存する"""
    with open(f"token_cache/{token_id}.json", "w") as f:
        json.dump(trait, f)


def get_eth_price(price):
    """weiをethに変換する"""
    wei = Decimal(price)
    eth = wei / Decimal(10**18)
    return eth


def main():
    token_id_to_price = get_listed_token_id_to_price()
    sorted_token_id_to_price = sorted(token_id_to_price.items(), key=lambda x: x[1])
    token_id_to_total_level = get_token_id_to_total_level(
        [token_id for token_id, price in sorted_token_id_to_price]
    )
    # トークンIDとその価格、トータルレベルをフロアプライス順にCSVに出力する
    with open("token_id_to_price_and_total_level.csv", "w") as f:
        f.write("token_id,price,total_level,url\n")
        for token_id, price in sorted_token_id_to_price:
            f.write(
                f"{token_id},{get_eth_price(price)},{token_id_to_total_level[token_id]},https://opensea.io/assets/ethereum/{CONTRACT_ADDRESS}/{token_id}\n"
            )


if __name__ == "__main__":
    main()
