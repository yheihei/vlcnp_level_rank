# NFT Collection Level Aggregator

特定のNFT（Non-Fungible Token）コレクションのリストされているアイテムのレベルを集計し、結果をCSVファイルに出力します。各NFTのレベルと価格を一覧で確認することができます。

## 使い方

### 環境変数の記載

```
cp .env-sample .env
# envの中の必要情報を記載
vim .env
```

### 必要パッケージインストール（for Mac）

```
brew install pipenv
pipenv --python 3
pipenv shell

pipenv install
```

### 実行コマンド

```
python main.py
```

## 出力結果

`token_id_to_price_and_total_level.csv` が出力される

```
token_id,price,total_level,url
3027,0.0088,28,https://opensea.io/assets/ethereum/0xCFE50e49ec3E5eb24cc5bBcE524166424563dD4E/3027
7014,0.0088,29,https://opensea.io/assets/ethereum/0xCFE50e49ec3E5eb24cc5bBcE524166424563dD4E/7014
7043,0.0089,26,https://opensea.io/assets/ethereum/0xCFE50e49ec3E5eb24cc5bBcE524166424563dD4E/7043
...
```
