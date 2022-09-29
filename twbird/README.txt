README

Install
=======
(a) Required postgres db - please install for your system
i.e. https://www.postgresql.org/download/macosx/
(b) After installing postres db run the following lines from the project dir (be sure to create the database tweetdw inside postrges first)
sudo -u postgres pg_ctl -D /Library/PostgreSQL/14/data start
(c) Update your config/base_settings.py with all the relevant connection info

(d)  SETUP YOUR DB
cd to project directory to run binaries
rm -rf migrations
flask shell
>>> from db.models import db
>>> db.drop_all()
>>> db.create_all()

(e) export your bearer token for twitter into your env
export BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAD0pfQEAAAAAGWJIXAzZZfCi8%2BeNVW51nnPohM0%3Dlh3XbMjhgYzxtWkjkeQq8WnGNHMPDyScszQWafBaxCKqN80Bsb

(1) pip install -r requirements.txt

cd to project directory to run binaries

cd tokeneer_2/twbird

(a) run the user management UI
waitress-serve --listen=*:9155 index:server

(b) run the web service
python ./twtsvc.py

(c) run the twitter capture
python ./get_user_tweets.py

(d) run the intervaled price snapper

python ./snap_prices.py

NOTES
=====

API Examples


1 - Follow a New User

curl --location --request POST 'http://localhost:5000/api/v1/followers' \
--data-raw '{
    "data": {
        "attributes": {
            "name": "yuisakov"
        }
    }
}'

2 - Get all Users
curl --location --request GET 'http://localhost:5000/api/v1/followers'

3 - Delete a User
curl --location --request DELETE 'http://localhost:5000/api/v1/followers/POTUS'

4 - Get all tweets
curl --location --request GET 'http://localhost:5000/api/v1/tweets'

5 - Get all tweets by User
curl --location --request GET 'http://localhost:5000/api/v1/tweets?name=yuisakov'


