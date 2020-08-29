import twitKeys as tk
import tweepy
import re
import openpyxl
import sys
import logging


def main():
    logging.basicConfig(level=logging.INFO,
                        format=' %(asctime)s - %(levelname)s - %(message)s')

    # Authorizing the app with the twitter dev app API keys
    auth = tweepy.OAuthHandler(tk.API_KEY, tk.API_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    # Regex for cleaning twitter's api data
    tweetAuthorRE = re.compile(r'\'([\d\w]+)\'')
    tweetLinkRE = re.compile(r'.*(https://t.co/[\w\d]*)')

    # Excel file for storing and comparing tweet data
    wb = openpyxl.load_workbook('twitLog.xlsx')
    sheet = wb.active

    # Counter for number of procesesed tweets
    tweetCount = 0
    # Counter for how many tweets in a row were previously logged
    prevLoggedCount = 0

    # Create a list of all existing tweet IDs
    tweetIDList = []
    for cell in list(sheet.columns)[0]:
        if cell.value is None:
            break
        tweetIDList.append(cell.value)

    User = sys.argv[1]
    # Using cursor, return a generator of 1 million of the user's favorited tweets
    for favorite in tweepy.Cursor(api.favorites, id=User).items(50):

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
            tweetDate = f'{favorite.created_at.year}-{favorite.created_at.month}-{favorite.created_at.day}'

            photos = []

            for medium in favorite.extended_entities['media']:
                if medium['type'] == 'photo' and len(medium['media_url']) > 0:
                    # Prints direct link of images within the tweet
                    photos.append(medium['media_url'])

            # If the tweet has not been logged, process it and reset the counter
            if not search_log(tweetIDList, tweetID):
                write_log(sheet, tweetID, author, tweetDate, tweetLink, photos)
                prevLoggedCount = 0

            # If it has been logged, increment the counter
            else:
                prevLoggedCount += 1

            # If there were 20 previously liked posts in a row, stop processing
            if prevLoggedCount > 20:
                break

            # Prints tweet information
            logging.info(f'Number: {tweetCount}')
            logging.info(f'Counter: {prevLoggedCount}')
            logging.info(f'Author: {author}')
            logging.info(f'ID: {tweetID}')
            logging.info(f'Link: {tweetLink}')
            logging.info(f'Date: {tweetDate}')
            for photo in photos:
                logging.info(f'Image: {photo}')


    wb.save('twitLog.xlsx')
    wb.close()

# Function to populate the excel file with twitter data from new tweets


def write_log(sheet, tweetID, author, tweetDate, tweetLink, photos):
    count = 0
    for photo in photos:
        count += 1
        sheet.insert_rows(1)
        sheet['A1'] = tweetID
        sheet['B1'] = author
        sheet['C1'] = tweetDate
        sheet['D1'] = '=HYPERLINK("{}", "{}")'.format(tweetLink, tweetLink)
        sheet['E1'] = '=HYPERLINK("{}", "{}")'.format(photo, photo)
        sheet['F1'] = count

# Function to search Excel to see if the tweet already exists in the database


def search_log(tweetIDList, tweetID):
    return tweetID in tweetIDList


if __name__ == "__main__":
    main()
