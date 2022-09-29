import os
import sys
from optparse import OptionParser
import configparser
from itertools import chain
import pandas as pd

from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert  # Important to use the postgresql insert
from db.models import Tweet, TokenPrice
from app import server, pgdb
from utils.helpers import call_repeat, getTokenPrice, getPairId

config = configparser.RawConfigParser()
with open("config/base_settings.py") as stream:
    stream = chain(("[DEFAULT]",), stream)
    config.read_file(stream)
    config = config['DEFAULT']
    config['HOST'] = config['HOST'].strip("'")

BEARER_TOKEN = config['BEARER_TOKEN']
EOD_HR_THRESHOLD = 23
INTRADAY_HR_THRESHOLD = 1

def compile_query(query):
    """Via http://nicolascadou.com/blog/2014/01/printing-actual-sqlalchemy-queries"""
    compiler = query.compile if not hasattr(query, 'statement') else query.statement.compile
    return compiler(dialect=postgresql.dialect())

def update(session, model, rows, as_of_date_col='report_date', no_update_cols=[]):
    table = model.__table__

    stmt = insert(table).values(rows)

    update_cols = [c.name for c in table.c
                   if c not in list(table.primary_key.columns)
                   and c.name not in no_update_cols]

    on_conflict_stmt = stmt.on_conflict_do_update(
        index_elements=table.primary_key.columns,
        set_={k: getattr(stmt.excluded, k) for k in update_cols}
        )

    #print(compile_query(on_conflict_stmt))
    session.execute(on_conflict_stmt)

def upsert_prices():
    now_utc = pd.Timestamp.utcnow()
    print(f'updating prices @ {now_utc} UTC')

    # get the first snapped tokens of the day
    queryString = """select distinct on ("token") * from tweet
                            where date(datetime) = CURRENT_DATE and "token" <> ''
                            order by "token", datetime asc;
                      """
    df_initial = pd.read_sql(queryString, con=pgdb.engine)

    tsQueryString = """select name, "token", datetime, price from tokpx
                            where date(datetime) = CURRENT_DATE 
                            and "token" = %(token_str)s
                            and name = %(name_str)s
                            order by datetime asc;
                      """

    # get the latest snapped tokens
    queryString = """select distinct on ("token") * from tokpx
                        where date(datetime) = CURRENT_DATE and "token" <> ''
                        order by "token", datetime desc;
                  """

    # has 24 hours passed since first snap of date
    remove_completed_tokens = df_initial[
        df_initial.priceChange.notna() |
        df_initial.priceChange1.notna() |
        df_initial.priceChange4.notna() |
        df_initial.priceChange12.notna() |
        df_initial.priceChange24.notna()].token.unique().tolist()
    df_initial = df_initial[~df_initial.token.isin(remove_completed_tokens)]

    # refresh query to get the latest snapped tokens
    df_latest = pd.read_sql(queryString, con=pgdb.engine)
    df_latest = df_latest[~df_latest.token.isin(remove_completed_tokens)]

    for id, name, tweet, datetime, token, price, priceChange, priceChange1, priceChange4, priceChange12, priceChange24, tweet_id, token_name, user_id in df_initial.itertuples(index=False):
        try:
            if (now_utc - datetime)>=pd.Timedelta(hours=EOD_HR_THRESHOLD) and (now_utc - datetime).components.minutes>=59:
                print(f'refreshing eod prices for token={token}, elapsed={(now_utc - datetime)}')
                px = getTokenPrice(token)
                price = px['data']['pairMetadata']['price']

                all_px = pd.read_sql(tsQueryString, con=pgdb.engine, params={'token_str': token, 'name_str': name})

                all_px['bt'] = all_px.datetime.dt.hour
                all_px = all_px.groupby('bt').nth([-1])
                all_px = all_px.reset_index().set_index(['bt']).reindex(pd.RangeIndex(24))
                if all_px.iloc[0].dropna().empty:
                    idx = all_px.first_valid_index()
                    all_px.iloc[0] = all_px.iloc[idx]

                #tweet = Tweet(name=name,
                #              tweet=tweet,
                #              datetime=now_utc,
                #              token=token,
                #              price=price,
                #              priceChange=all_px.iloc[1].price.item()/all_px.iloc[0].price.item() - 1,
                #              priceChange1=all_px.iloc[1].price.item()/all_px.iloc[0].price.item() - 1,
                #              priceChange4=all_px.iloc[4].price.item()/all_px.iloc[0].price.item() - 1,
                #              priceChange12=all_px.iloc[12].price.item()/all_px.iloc[0].price.item() - 1,
                #              priceChange24=float(price)/all_px.iloc[0].price.item() - 1,
                #              )
                #with server.app_context():
                #    tweet.add(tweet)
                update_rows = [
                    [id,
                     name,
                     tweet,
                     datetime,
                     token,
                     price,
                     all_px.iloc[1].price.item()/all_px.iloc[0].price.item() - 1,
                     all_px.iloc[1].price.item()/all_px.iloc[0].price.item() - 1,
                     all_px.iloc[4].price.item()/all_px.iloc[0].price.item() - 1,
                     all_px.iloc[12].price.item()/all_px.iloc[0].price.item() - 1,
                     float(price)/all_px.iloc[0].price.item() - 1]
                ]
                update(pgdb.engine, Tweet, update_rows, no_update_cols=['id', 'name', 'tweet', 'datetime', 'token', 'price'])

        except Exception as e:
            print(e)

    # has some prededfined bar interval passed since the last token was updated (i.e. we need a fresh price)
    for id, tweet, datetime, token, price in df_latest.itertuples(
            index=False):

        try:
            if (now_utc - datetime) >= pd.Timedelta(hours=INTRADAY_HR_THRESHOLD):
                print(f'refreshing prices for token={token}')
                px = getTokenPrice(token)
                price = px['data']['pairMetadata']['price']
                tweet = TokenPrice(name=name,
                              datetime=now_utc,
                              token=token,
                              price=price,
                              )
                with server.app_context():
                    tweet.add(tweet)

        except Exception as e:
            print(e)


def main():
    op = OptionParser()
    op.add_option('--token', dest='token', default=None, help='bearer token')
    op.add_option('--user', dest='users', action='append', default=[], help='users to follow')
    op.add_option('--interval', dest='interval', type=int, default=10, help='interval in secs to snapshot')

    (opts, args) = op.parse_args()

    global BEARER_TOKEN
    if opts.token:
        BEARER_TOKEN = opts.token
    BEARER_TOKEN = BEARER_TOKEN.strip('\"')

    cancel_future_calls = call_repeat(opts.interval, upsert_prices)
    cancel_future_calls()


if __name__ == '__main__':
    main()
