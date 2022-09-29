import os
import sys
from optparse import OptionParser
from tweepy import StreamingClient, StreamRule
import requests
import configparser
from itertools import chain
from requests.structures import CaseInsensitiveDict
import threading
import urllib
import re
import json
from config.base_settings import BEARER_TOKEN
from utils.helpers import call_repeat, getTokenPrice

config = configparser.RawConfigParser()
with open("config/base_settings.py") as stream:
    stream = chain(("[DEFAULT]",), stream)
    config.read_file(stream)
    config = config['DEFAULT']
    config['HOST'] = config['HOST'].strip("'")

threadLock = threading.Lock()
FOLLOWERS = []

def getTokensMentioned(tweet):
    def getCryptoID(url):
        if "https://dextools.io/app/ether/pair-explorer/" in url:
            return url.split("/")[-1]

        return None

    urls = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", tweet)

    tokens_mentioned = []
    for url in urls:
        try:
            actual_url = requests.get(url).url
            crypto_id = getCryptoID(actual_url)
            if crypto_id:
                tokens_mentioned.append(crypto_id)

        except:
            actual_url = url
            crypto_id = getCryptoID(actual_url)
            if crypto_id:
                tokens_mentioned.append(crypto_id)

    return tokens_mentioned


def userid2username(userid):
    try:
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
        response = requests.get(f"https://api.twitter.com/2/users/{userid}", headers=headers, timeout=5)
        response.raise_for_status()
        userdata = response.json()['data']['username']
        return userdata
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)


def get_followers():
    try:
        response = requests.get(f"http://{config['HOST']}:{config['PORT']}/api/v1/followers", timeout=5)
        response.raise_for_status()
        followers = response.json()
        return followers
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)


def post_tweet(tweet):
    try:
        response = requests.post(f"http://{config['HOST']}:{config['PORT']}/api/v1/tweets",
                                 data=tweet,
                                 timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)

def post_tweet_to_app(tweet):
    print("SENDING...")
    try:
        URL = "http://localhost:5000/api/post_new_tweets"
        print(URL)
        response = requests.post(URL,
                                 json=tweet,
                                 timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)

def post_token(tweet):
    try:
        response = requests.post(f"http://{config['HOST']}:{config['PORT']}/api/v1/tokens",
                                 data=tweet,
                                 timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)

def update_followers():
    followers = get_followers()
    with threadLock:
        global FOLLOWERS
        FOLLOWERS = [f['attributes']['screen_name'] for f in followers]
        FOLLOWERS = list(set(FOLLOWERS))


def create_tweet(tweet, token=None, px=None):

    nonLiquidityToken = px['data']['pairMetadata']['nonLiquidityToken'] if px else None

    tweet = {
        "data": {
            "attributes": {
                "name": userid2username(tweet.author_id),
                "user_id": tweet.author_id,
                "text": tweet.text,
                "token": token,
                "price": px['data']['pairMetadata']['price'] if px else None,
                "token_name": px['data']['pairMetadata'][nonLiquidityToken]['symbol'] if px else None,
                #"priceChange": px['data']['pairMetadata']['priceChange'] if px else None,
                #"priceChange1": px['data']['pairMetadata']['priceChange1'] if px else None,
                #"priceChange4": px['data']['pairMetadata']['priceChange4'] if px else None,
                #"priceChange12": px['data']['pairMetadata']['priceChange12'] if px else None,
                #"priceChange24": px['data']['pairMetadata']['priceChange24'] if px else None,
                "priceChange": None,
                "priceChange1": None,
                "priceChange4": None,
                "priceChange12": None,
                "priceChange24": None,
                "created_at": f'{tweet.created_at}',
                "tweet_id": str(tweet.id),
                "id": tweet.id
            }
        }
    }
    return tweet

def create_crypto(tweet, token=None, px=None):
    tweet = {
        "data": {
            "attributes": {
                "name": userid2username(tweet.author_id),
                "token": token,
                "price": px['data']['pairMetadata']['price'] if px else None,
                "created_at": f'{tweet.created_at}'
            }
        }
    }
    return tweet


class TweetStreamV2(StreamingClient):

    def on_tweet(self, tweet):
        print(f"{tweet.id} {tweet.created_at} ({tweet.author_id}): {tweet.text}")
        print("-" * 50)

        token = ''
        px = None
        try:
            asset_tokens = getTokensMentioned(tweet.text)
            if not asset_tokens:
                raise

            for token in asset_tokens:
                try:
                    px = getTokenPrice(token)
                except:
                    px = None

                ### TWEET ###
                twt = create_tweet(tweet, token, px)
                post_tweet(json.dumps(twt))
                print("Posting tweet data to app...")
                post_tweet_to_app(json.dumps(twt))

                ### TOKEN ###
                twt = create_crypto(tweet, token, px)
                post_token(json.dumps(twt))
        except:
            print("Tweet did not contain a token.")
            # twt = create_tweet(tweet, token, px)
            # post_tweet(json.dumps(twt))

    def on_errors(self, errors):
        print(f"Received error code {errors}")
        self.disconnect()
        return False

    def on_connection_error(self):
        self.disconnect()


printer = None


def listen_tweets():
    global printer

    global FOLLOWERS
    update_followers()

    userfilters = []
    with threadLock:
        for user in FOLLOWERS:
            userfilters.append(f'from:{user}')
    userfilters = ' OR '.join(userfilters)

    if printer:
        printer.disconnect()
        del printer

    printer = TweetStreamV2(bearer_token=BEARER_TOKEN,
                            wait_on_rate_limit=True)
    rules = printer.get_rules()

    # Rules persist on Twitter’s end unless you delete them,
    # so if you’ve previously added rules without doing so they’re still there
    if rules.data:
        rule_ids = []
        for rule in rules.data:
            print(f"rule marked to delete: {rule.id} - {rule.value}")
            rule_ids.append(rule.id)
        if len(rule_ids) > 0:
            printer.delete_rules(rule_ids)
            printer.disconnect()
            del printer

            printer = TweetStreamV2(bearer_token=BEARER_TOKEN,
                                    wait_on_rate_limit=True)
        else:
            print("no rules to delete")

    print(f"Streaming Tweets from selected users:{FOLLOWERS} ...")
    # add rules
    printer.add_rules([
        StreamRule(f"{userfilters} -is:retweet")
    ])

    printer.filter(expansions="author_id",
                   tweet_fields=['created_at'],
                   user_fields=['name', 'username', 'id'],
                   threaded=False
                   )

import tweepy

def update_influencers():
    print("UPDATEING INFLUENCERS")

    followers = get_followers()
    with threadLock:
        global FOLLOWER_IDS
        FOLLOWER_IDS = [f['attributes']['user_id'] for f in followers]
        FOLLOWER_IDS = list(set(FOLLOWER_IDS))
    
        print(FOLLOWER_IDS)

        ### >>> GET INFLUENCER DATA <<< ###
        API_KEY = 'zC4jO7rwJKgpSEk1Gea0Gn2UA'
        API_SECRET = 'W6GznkKdvmQJcW0SKu4SyuQ8oc3RIeopAnyrQKqfkJKMJkXo8s'
        ACCESS_TOKEN = '813561826629730304-blDojTpFwVvANOwv0GZwQiWQvHQXJ7s'
        ACCESS_TOKEN_SECRET = 'FEce0d2fGuty28hL81PssYmHqpLXrgx9EyquDpdbxi6Im'


        # Variables that contains the user credentials to access Twitter API 
        access_token = ACCESS_TOKEN
        access_token_secret = ACCESS_TOKEN_SECRET
        consumer_key = API_KEY
        consumer_secret = API_SECRET

        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
        api = tweepy.API(auth)
        
        for id in FOLLOWER_IDS:
            api.get_user(user_id=id)

        # user = api.get_user(user_id='813561826629730304') #### => This can be used every night to update the influencer data
        # user = api.get_user(user_id=follower_dict['name'])
        ### >>> GET INFLUENCER DATA <<< ###

def main():
    op = OptionParser()
    op.add_option('--token', dest='token', default=None, help='bearer token')
    op.add_option('--user', dest='users', action='append', default=[], help='users to follow')
    (opts, args) = op.parse_args()

    global BEARER_TOKEN
    if opts.token:
        BEARER_TOKEN = opts.token

    BEARER_TOKEN = BEARER_TOKEN.strip('\"')

    global FOLLOWERS
    FOLLOWERS.extend(opts.users)

    update_followers()
    # update_influencers()

    cancel_future_calls = call_repeat(30, listen_tweets)
    cancel_future_calls()


if __name__ == '__main__':
    main()
