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

    count = 0

    User = "@edzbrys"
    # Using cursor, return a generator of 1 million of the user's favorited tweets
    for favorite in tweepy.Cursor(api.favorites, id=User).items(5): #1000000):

        # Counter for number of tweets processed
        count += 1

        if 'media' in favorite.entities:
            for medium in favorite.extended_entities['media']:
                if medium['type'] == 'photo':

                    print(f'\n\nNumber: {count}')

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

                    # Prints direct link of images within the tweet
                    print('Image:', medium['media_url'])


# Function to populate the excel file with twitter data from new tweets
def writeExcel():
    pass

# Function to search Excel to see if excel 
def searchExcel():
    pass


if __name__ == "__main__":
    main()
