import json
from flask_restful import Resource
from marshmallow import ValidationError
from db.models import db, Tweet, TweetSchema
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, make_response, request, abort

schema = TweetSchema()


class TweetList(Resource):

    def get(self):
        '''
        http://jsonapi.org/format/#fetching
        A server MUST respond to a successful request to fetch an individual resource or resource collection
        with a 200 OK response.
        A server MUST respond with 404 Not Found when processing a request to fetch a single resource that
        does not exist, except when the request warrants a 200 OK response with null as the primary data
        (as described above) a self link as part of the top-level links object
        '''
        name = request.args.get('user_id')
        is_token = request.args.get('isToken', default=False, type=lambda v: v.lower() == 'true')
        if name:
            if is_token:
                query = Tweet.query.filter_by(token=name).all()
            else:
                query = Tweet.query.filter_by(user_id=name).all()
        else:
            query = Tweet.query.all()
        results = schema.dump(query, many=True)['data']
        return results, 200

    def post(self):
        '''
        http://jsonapi.org/format/#crud
        A resource can be created by sending a POST request to a URL that represents a collection of resources.
        The request MUST include a single resource object as primary data. The resource object MUST contain at
        least a type member.
        If a POST request did not include a Client-Generated ID and the requested resource has been created
        successfully, the server MUST return a 201 Created status code
        '''
        raw_dict = request.get_json(force=True)
        try:
            # Validate Data
            schema.validate(raw_dict)

            # Save the new follower
            follower_dict = raw_dict['data']['attributes']
            
            tweet = Tweet(name=follower_dict['name'],
                          user_id=follower_dict['user_id'],
                          tweet=follower_dict['text'],
                          datetime=follower_dict['created_at'],
                          token=follower_dict.get('token', ''),
                          token_name=follower_dict.get('token_name', ''),
                          price=follower_dict.get('price', None),
                          priceChange=follower_dict.get('priceChange', None),
                          priceChange1 = follower_dict.get('priceChange1', None),
                          priceChange4 = follower_dict.get('priceChange4', None),
                          priceChange12 = follower_dict.get('priceChange12', None),
                          priceChange24=follower_dict.get('priceChange24', None),
                          tweet_id = str(follower_dict['id'])
                        )
            tweet.add(tweet)

            # Return the new information
            query = Tweet.query.get(tweet.id)
            results = schema.dump(query)['data']
            return results, 201

        except ValidationError as err:
            resp = jsonify({"error": err.messages})
            resp.status_code = 403
            return resp

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = 403
            return resp
