import pytz, datetime
from marshmallow import validate
from sqlalchemy.orm import validates
from flask_sqlalchemy import SQLAlchemy
from marshmallow_jsonapi import Schema, fields

# Prepare the database
db = SQLAlchemy()


#############################################
########## Utility Classes/Constants
#############################################

# Class to add, update and delete data via SQLALchemy sessions
class CRUD():

    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()


NOT_BLANK = validate.Length(min=1, error='Field cannot be blank')


#############################################
########## Models
#############################################

class Follower(db.Model, CRUD):
    __tablename__ = 'follower'

    id                  = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String(255), unique=False)
    follower_count      = db.Column(db.Integer,     unique=False)
    user_id             = db.Column(db.String(255), unique=True )
    screen_name         = db.Column(db.String(255), unique=False)
    profile_banner_url  = db.Column(db.String(),    unique=False)
    profile_image_url   = db.Column(db.String(),    unique=False)
    verified            = db.Column(db.Boolean,     unique=False)

    def __repr__(self):
        return f'<models.Follower[name={self.name}]>'


class FollowerSchema(Schema):
    # Validation for the different fields
    id                  = fields.Integer(dump_only=True)
    name                = fields.String(validate=NOT_BLANK)
    follower_count      = fields.Integer(validate=NOT_BLANK)
    user_id             = fields.String(validate=NOT_BLANK)
    screen_name         = fields.String(validate=NOT_BLANK)
    verified            = fields.Boolean(validate=NOT_BLANK)
    profile_banner_url  = fields.String(validate=NOT_BLANK)
    profile_image_url   = fields.String(validate=NOT_BLANK)

    class Meta:
        type_ = 'follower'


class Tweet(db.Model, CRUD):
    __tablename__ = 'tweet'

    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.String(255), unique=False)
    name = db.Column(db.String(255), unique=False)
    user_id = db.Column(db.String(255), unique=False)
    tweet = db.Column(db.String(255), unique=False)
    datetime = db.Column(db.DateTime(timezone=True), unique=False)
    token = db.Column(db.String(255), unique=False)
    token_name = db.Column(db.String(255), unique=False)
    price = db.Column(db.Float(), unique=False)
    priceChange = db.Column(db.Float(), unique=False)
    priceChange1 = db.Column(db.Float(), unique=False)
    priceChange4 = db.Column(db.Float(), unique=False)
    priceChange12 = db.Column(db.Float(), unique=False)
    priceChange24 = db.Column(db.Float(), unique=False)

    def __repr__(self):
        return f'<models.Tweet[name={self.name},tweet={self.tweet}]>'


class TweetSchema(Schema):
    # Validation for the different fields
    id = fields.Integer(dump_only=True)
    tweet_id =  fields.String()
    name = fields.String(validate=NOT_BLANK)
    user_id = fields.String(validate=NOT_BLANK)
    tweet = fields.String(validate=NOT_BLANK)
    datetime = fields.DateTime(validate=NOT_BLANK)
    token = fields.String()
    token_name = fields.String()
    price = fields.Float()
    priceChange = fields.Float()
    priceChange1 = fields.Float()
    priceChange4 = fields.Float()
    priceChange12 = fields.Float()
    priceChange24 = fields.Float()

    class Meta:
        type_ = 'tweet'


class TokenSchema(Schema):
    # Validation for the different fields
    id = fields.Integer(dump_only=True)
    token = fields.List(fields.String())

    class Meta:
        type_ = 'token'

class TokenPrice(db.Model, CRUD):
    __tablename__ = 'tokpx'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False)
    datetime = db.Column(db.DateTime(timezone=True), unique=False)
    token = db.Column(db.String(255), unique=False)
    price = db.Column(db.Float(), unique=False)

    def __repr__(self):
        return f'<models.TokenPrices[name={self.name},token={self.tweet},px={self.price}]>'


class TokenPricesSchema(Schema):
    # Validation for the different fields
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=NOT_BLANK)
    datetime = fields.DateTime(validate=NOT_BLANK)
    token = fields.String()
    price = fields.Float()

    class Meta:
        type_ = 'tokpx'
