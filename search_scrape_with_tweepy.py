# -- coding: utf-8 -
# Written by Ibrahim Aderinto

'''
This script is for scraping tweets from twitter search results given some keywords for searching.
'''

from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
from credentials import *
from datetime import datetime

def get_details(file):
    with open(file) as f:
        keywords = [i[:-2].replace(',', ' ').strip() for i in f.readlines()][1:]
    return keywords


def get_tweets(auth_api, keyword, month):
    result_writer = open(keyword+'.csv', 'w')
    result_writer.write('Tweets')
    
    for tweet in Cursor(auth_api.search_full_archive, environment_name='',  q=keyword).items():
        month_created = tweet.created_at.month
        if month_created < month:
            break
        elif month_created == month:
            tweet = tweet.full_text
            tweet.replace('\n', ' ')
            result_writer.write(tweet)


def main(auth_api):
    # Reading keywords from the csv file
    keywords = get_details('data_file.csv')

    # Getting the last month from current month
    start_date = datetime.now()
    month = start_date.month
    if month == 1:
        month = 12
    else:
        month -= 1
    
    for keyword in keywords:
        if keyword == '':
            continue
        print(f"Scraping for {keyword}")
        get_tweets(auth_api, keyword, month)


if __name__=='__main__':
    auth = OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    auth_api = API(auth)
    main(auth_api)
