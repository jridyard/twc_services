from threading import Event, Thread, Timer
import requests

def call_repeat(interval, func, *args):
    stopped = Event()

    def loop():
        while not stopped.wait(interval):
            func(*args)

    Thread(target=loop()).start()
    return stopped.set

def getPairId(crypto_id):
    headers = {
        'x-api-key': 'da2-vkmqkh3wlngdfktfeybq6j44li',
    }
    json_data = {
        'operationName': 'Search',
        'variables': {
            'limit': 10,
            'lowVolumeFilter': True,
            'networkFilter': [
                1,
                56,
                43114,
                250,
                137,
                1666600000,
                42161,
                10,
                25,
                42220,
                1313161554,
                1284,
                1285,
                9001,
                128,
                1088,
                100,
                592,
                42262,
                53935,
                288,
                4689,
                66,
                888,
                321,
                106,
                10000,
                24,
                122,
                20,
                2001,
                1030,
                3000,
                333999,
                55,
                70,
                57,
                8217,
                336,
                40,
                246,
                820,
            ],
            'resolution': '1D',
            'search': crypto_id,
        },
        'query': 'query Search($search: String!, $networkFilter: [Int!], $lowVolumeFilter: Boolean, $resolution: String, $limit: Int) {\n  search(\n    search: $search\n    networkFilter: $networkFilter\n    lowVolumeFilter: $lowVolumeFilter\n    resolution: $resolution\n    limit: $limit\n  ) {\n    hasMore\n    hasMoreLowVolume\n    tokens {\n      ...BaseTokenWithMetadata\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment BaseTokenWithMetadata on TokenWithMetadata {\n  address\n  decimals\n  id\n  liquidity\n  name\n  networkId\n  price\n  priceChange\n  priceChange24\n  priceChange12\n  priceChange4\n  priceChange1\n  resolution\n  symbol\n  volume\n  topPairId\n  exchanges {\n    ...ExchangeModel\n    __typename\n  }\n  __typename\n}\n\nfragment ExchangeModel on Exchange {\n  address\n  color\n  exchangeVersion\n  id\n  name\n  networkId\n  tradeUrl\n  iconUrl\n  enabled\n  __typename\n}\n',
    }
    response = requests.post('https://i3zwhsu375dqllo5srv5vn35ba.appsync-api.us-west-2.amazonaws.com/graphql',
                             headers=headers, json=json_data)
    return response.json()['data']['search']['tokens'][0]['topPairId']


def getTokenPrice(crypto_id):
    headers = {
        'x-api-key': 'da2-vkmqkh3wlngdfktfeybq6j44li',
    }
    json_data = {
        'operationName': 'GetPairMetadata',
        'variables': {
            'pairId': getPairId(crypto_id),
        },
        'query': 'query GetPairMetadata($pairId: String!) {\n  pairMetadata(pairId: $pairId) {\n    price\n    exchangeId\n    fee\n    id\n    liquidity\n    liquidityToken\n    nonLiquidityToken\n    pairAddress\n    priceChange\n    priceChange1\n    priceChange12\n    priceChange24\n    priceChange4\n    tickSpacing\n    volume\n    volume1\n    volume12\n    volume24\n    volume4\n    token0 {\n      address\n      decimals\n      name\n      networkId\n      pooled\n      price\n      symbol\n      __typename\n    }\n    token1 {\n      address\n      decimals\n      name\n      networkId\n      pooled\n      price\n      symbol\n      __typename\n    }\n    __typename\n  }\n}\n',
    }
    response = requests.post('https://i3zwhsu375dqllo5srv5vn35ba.appsync-api.us-west-2.amazonaws.com/graphql',
                             headers=headers, json=json_data)
    return response.json()
