import twitKeys as tk
import tweepy
import re
import openpyxl
import pandas as pd
import sys


def main():

    # Authorizing the app with the twitter dev app API keys
    auth = tweepy.OAuthHandler(tk.API_KEY, tk.API_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    # Regex for cleaning twitter's api data
    tweetAuthorRE = re.compile(r'\'([\d\w]+)\'')
    tweetLinkRE = re.compile(r'.*(https://t.co/[\w\d]*)')

    # Excel database for storing and comparing tweet data

    # Counter for number of procesesed tweets
    tweetCount = 0
    # Counter for how many tweets in a row were previously logged
    prevLoggedCount = 0

    # Take the username of the account to be processed
    try:
        User = sys.argv[1]
    except:
        print('Missing command line args')
        return

    db = pd.read_excel('twitDB.xlsx', dtype={'tweetID': str})

    rowsAppend = []

    # Using cursor, return a generator of 1 million of the user's favorited tweets
    for favorite in tweepy.Cursor(api.favorites, id=User).items(1000000):

        # Counter for number of tweets processed
        tweetCount += 1

        # Check if the tweet includes an image
        is_image = False
        if 'media' in favorite.entities:
            for medium in favorite.extended_entities['media']:
                if medium['type'] == 'photo' and len(medium['media_url']) > 0:
                    is_image = True
                    break

        # Process the tweet if it includes an image
        if is_image:

            # Regex searching of the tweet author and tweet link
            authorRAW = str(favorite.user.screen_name.encode("utf-8"))
            tweetText = str(favorite.text.encode("utf-8"))
            try:
                tweetLink = tweetLinkRE.search(tweetText)[1]
            except:
                tweetLink = tweetText
            try:
                author = tweetAuthorRE.search(authorRAW)[1]
            except:
                author = authorRAW

            tweetID = str(favorite.id)
            date = f'{favorite.created_at.year}-{favorite.created_at.month}-{favorite.created_at.day}'

            photos = []

            for medium in favorite.extended_entities['media']:
                if medium['type'] == 'photo' and len(medium['media_url']) > 0:
                    # Prints direct link of images within the tweet
                    photos.append(medium['media_url'])

            # If the tweet is not in the database, process it and reset the counter
            if not search_db(db, tweetID):
                write_db(rowsAppend, tweetID, author, date, tweetLink, photos)
                prevLoggedCount = 0

            # If it is in the database, increment the counter
            else:
                prevLoggedCount += 1

            # If there were 20 previously logged posts in a row, stop processing
            if prevLoggedCount > 20:
                break

            # Prints tweet information


    db = db.append(rowsAppend)
    db.sort_values(by=['tweetID'])
    print(db.head(1000000))

    db.to_excel('twitDB.xlsx', index=False)


# Function to populate the excel file with twitter data from new tweets
def write_db(rowsAppend, tweetID, author, date, tweetLink, photos):
    count = 0
    for imageLink in photos:
        count += 1
        rowsAppend.append({'tweetID': tweetID, 'author': author, 'date': date,
                           'link': tweetLink, 'imageLink': imageLink, 'count': count})


# Function to search Excel to see if the tweet already exists in the database
def search_db(db, tweetID):
    return tweetID in set(db["tweetID"])


if __name__ == "__main__":
    main()
