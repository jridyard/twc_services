import json
from flask_restful import Resource
from marshmallow import ValidationError
from db.models import db, Tweet, TokenPricesSchema, TokenPrice
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, make_response, request, abort
from sqlalchemy import select

schema = TokenPricesSchema()


class TokenList(Resource):

    def get(self):
        '''
        http://jsonapi.org/format/#fetching
        A server MUST respond to a successful request to fetch an individual resource or resource collection
        with a 200 OK response.
        A server MUST respond with 404 Not Found when processing a request to fetch a single resource that
        does not exist, except when the request warrants a 200 OK response with null as the primary data
        (as described above) a self link as part of the top-level links object
        '''
        query = db.session.query(Tweet.token).all()
        results = list(set([tok[0].strip() for tok in query if tok[0].strip()]))
        return jsonify({
            'type': 'token',
            'attributes': {
                'tokens': results
            }
        })


class TokenPrices(Resource):

    def post(self):
        '''
        http://jsonapi.org/format/#crud
        A resource can be created by sending a POST request to a URL that represents a collection of resources.
        The request MUST include a single resource object as primary data. The resource object MUST contain at
        least a type member.
        If a POST request did not include a Client-Generated ID and the requested resource has been created
        successfully, the server MUST return a 201 Created status code
        '''

        print("TOKEN PRICES RUNNING")

        raw_dict = request.get_json(force=True)
        
        print(raw_dict)

        try:
            # Validate Data
            schema.validate(raw_dict)

            print("Made it this far")

            # Save the new follower
            follower_dict = raw_dict['data']['attributes']

            print("??????")

            tweet = TokenPrice(
                        name=follower_dict['name'],
                        datetime=follower_dict['created_at'],
                        token=follower_dict.get('token', ''),
                        price=follower_dict.get('price', None)
                    )

            print("???!!!!!!")
            tweet.add(tweet)

            print("Still going")

            # Return the new information
            query = TokenPrice.query.get(tweet.id)
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
