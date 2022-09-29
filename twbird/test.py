import tweepy

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

# user = api.get_user(user_id='813561826629730304') #### => This can be used every night to update the influencer data
user = api.lookup_users(screen_name=['jmridyard', 'elonmusk'])
### >>> GET INFLUENCER DATA <<< ###

print(user[1].id)