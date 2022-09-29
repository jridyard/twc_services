#! /usr/bin/env python
from flask import Flask
from v1api import v1
from db.models import db

app = Flask(__name__)

from flask_cors import CORS
CORS(app)

#############################################
########## App Configuration
#############################################
app.config.from_object('config.base_settings')

#############################################
########## Blueprints
#############################################
app.register_blueprint(v1, url_prefix='/api/v1')

#############################################
########## Database
#############################################
db.init_app(app)

if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            debug=app.config['DEBUG'],
            threaded=True,
            port=app.config['PORT']
            )
