import json
from flask_restful import Resource
from marshmallow import ValidationError
from db.models import db, Follower, FollowerSchema
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, make_response, request, abort
import tweepy

schema = FollowerSchema()


class FollowerList(Resource):

    def get(self):
        '''
        http://jsonapi.org/format/#fetching
        A server MUST respond to a successful request to fetch an individual resource or resource collection
        with a 200 OK response.
        A server MUST respond with 404 Not Found when processing a request to fetch a single resource that
        does not exist, except when the request warrants a 200 OK response with null as the primary data
        (as described above) a self link as part of the top-level links object
        '''
        query = Follower.query.all()
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
            follower_dict = raw_dict['data']['attributes']
            
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
            user = api.get_user(screen_name=follower_dict['name'])
            ### >>> GET INFLUENCER DATA <<< ###

            # Validate Data
            schema.validate(raw_dict)

            # Save the new follower
            follower = Follower(
                name=user.name,
                follower_count=user.followers_count,
                user_id=user.id,
                screen_name=user.screen_name,
                verified=user.verified
            )

            already_exists = Follower.query.filter_by(user_id=str(user.id)).first()
            if already_exists:
                return schema.dump(already_exists, many=False), 200

            follower.add(follower)

            # Return the new information
            query = Follower.query.get(follower.id)
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


class FollowerUpdate(Resource):

    def get(self, user_id):
        '''
        http://jsonapi.org/format/#fetching
        A server MUST respond to a successful request to fetch an individual resource or resource collection with
        a 200 OK response.
        A server MUST respond with 404 Not Found when processing a request to fetch a single resource that does not
        exist, except when the request warrants a 200 OK response with null as the primary data (as described above)
        a self link as part of the top-level links object
        '''
        try:
            query = Follower.query.filter_by(user_id=user_id).first_or_404()
            result = schema.dump(query)['data']
            return result
        except KeyError as err:
            abort(404)

    def delete(self, user_id):
        '''
        http://jsonapi.org/format/#crud-deleting
        A server MUST return a 204 No Content status code if a deletion request is successful and no content is returned.
        '''
        try:
            follower = Follower.query.filter_by(user_id=user_id).first_or_404()
            delete = follower.delete(follower)
            response = make_response()
            response.status_code = 204
            return response

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = 401
            return resp
