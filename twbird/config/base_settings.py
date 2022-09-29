# Flask Core Settings
APP_NAME = "TweetDW"
DEBUG = True
HOST = '127.0.0.1'
PORT = 5050
SECRET_KEY = "FEce0d2fGuty28hL81PssYmHqpLXrgx9EyquDpdbxi6Im"
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAADUNfQEAAAAAhxGSAQfzuie%2BLwXdvg4Ko9o2SkE%3DHeYRFLW8W84QAev8qXjz8tFLGfY1RfNUBFiohQ0lLkSniqrN5p'
if not BEARER_TOKEN:
    import os
    BEARER_TOKEN = os.getenv('BEARER_TOKEN')
    BEARER_TOKEN = BEARER_TOKEN.strip('\"')

# Database Settings
DB_USER = 'postgres'
DB_PASS = 'dbpass123'
DB_HOST = 'localhost'
DB_NAME = 'tweetdw'

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'.format(
    DB_USER=DB_USER,
    DB_PASS=DB_PASS,
    DB_HOST=DB_HOST,
    DB_NAME=DB_NAME)
SQLALCHEMY_TRACK_MODIFICATIONS = False