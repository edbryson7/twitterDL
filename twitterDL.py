import twitKeys as tk
import tweepy
import time
import re


def main():
    auth = tweepy.OAuthHandler(tk.API_KEY, tk.API_SECRET)
    api = tweepy.API(auth)

    tweetAuthorRE = re.compile(r'\'([\d\w]+)\'')
    tweetLinkRE = re.compile(r'.*(https://t.co/[\w\d]*)')

    count = 0
    # This variable hold the username or the userid of the user you want to get favorites from
    # This needs to be the users unique username
    User = "@edzbrys"
    # Using cursor, return a generator of 1 million of the user's favorited tweets
    for favorite in tweepy.Cursor(api.favorites, id=User).items(1000000):
        # time variable used for delaying
        now = time.time()

        #counter for number of tweets processed
        count += 1
        print(f'\n\nNumber: {count}')

        # Regex searching of the tweet author and tweet link
        authorRAW = str(favorite.user.screen_name.encode("utf-8"))
        author = tweetAuthorRE.search(authorRAW)[1]
        tweetText = str(favorite.text.encode("utf-8"))
        tweetLink = tweetLinkRE.search(tweetText)[1]

        tweetID = str(favorite.id)

        # Prints tweet information
        print(f'Author: {author}')
        print(f'Id: {tweetID}')
        print(f'Link: {tweetLink}')
        print(
            f'Date: {favorite.created_at.year}-{favorite.created_at.month}-{favorite.created_at.day}')

        # Prints direct link of images within the tweet
        if 'media' in favorite.entities:
            for medium in favorite.extended_entities['media']:
                if medium['type'] == 'photo':
                    print('Tweet Image:', medium['media_url'])

        # Delay to avoid going over twitter API rate limit
        while(time.time() - now <= 3):
            time.sleep(0.1)

if __name__ == "__main__":
    main()
