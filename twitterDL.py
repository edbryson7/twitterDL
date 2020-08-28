import twitKeys as tk
import tweepy
import re
import openpyxl


def main():
    # Authorizing the app with the twitter dev app API keys
    auth = tweepy.OAuthHandler(tk.API_KEY, tk.API_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

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


    User = "@edzbrys"
    # Using cursor, return a generator of 1 million of the user's favorited tweets
    for favorite in tweepy.Cursor(api.favorites, id=User).items(5): #1000000):

        # Counter for number of tweets processed
        tweetCount += 1

        is_image = False

        if 'media' in favorite.entities:
            for medium in favorite.extended_entities['media']:
                if medium['type'] == 'photo' and len(medium['media_url'])>0:
                    is_image = True
                    break
        if is_image:
            print(f'\n\nNumber: {tweetCount}')

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

            # Prints tweet information
            print(f'Author: {author}')
            print(f'ID: {tweetID}')
            print(f'Link: {tweetLink}')
            print(f'Date: {tweetDate}')

            photos = []

            for medium in favorite.extended_entities['media']:
                if medium['type'] == 'photo' and len(medium['media_url'])>0:
                    # Prints direct link of images within the tweet
                    print('Image:', medium['media_url'])
                    photos.append(medium['media_url'])

            # First see if the tweet is already in the excel log
            if not search_log(tweetID):
                prevLoggedCount += 1
                write_log(tweetID, author, tweetDate, tweetLink, photos)

    wb.save('twitLog.xlsx')
    wb.close()


# Function to populate the excel file with twitter data from new tweets
def write_log(tweetID, author, tweetDate, tweetLink, photos):
    pass

# Function to search Excel to see if the tweet already exists in the database
def search_log(tweetID):
    pass


if __name__ == "__main__":
    main()
