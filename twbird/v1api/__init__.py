from flask import Blueprint, abort, jsonify
from flask_restful import Api
from v1api.resources.follower import FollowerList, FollowerUpdate
from v1api.resources.tweet import TweetList
from v1api.resources.token import TokenList, TokenPrices

# Declare the blueprint
v1 = Blueprint('v1', __name__)

# Set up the API and init the blueprint
api = Api()
api.init_app(v1)

#############################################
########## Resources to Add
#############################################

# Followers
api.add_resource(FollowerList, '/followers')
api.add_resource(FollowerUpdate, '/followers/<string:user_id>')

# Tweets
api.add_resource(TweetList, '/tweets')

# Tokens
api.add_resource(TokenList, '/tokens')
api.add_resource(TokenPrices, '/tokens')