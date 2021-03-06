import twitKeys as tk
import tweepy
import re
import openpyxl
import pandas as pd
import sys
import requests
import os


def main():
    # Take the username of the account to be processed
    try:
        User = sys.argv[1]
    except:
        print('Missing command line args')
        return

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
    # Counter for successfully downloaded images
    goodDL = 0
    # Counter for unsuccessfully downloaded images
    badDL = 0

    # Remove hyperlinks so that pandas can read the data
    remove_hyperlinks()

    # Read the excel database
    db = pd.read_excel('twitDB.xlsx', dtype={'tweetID': str})

    # List for storing dictionaries of pandas data for later writing to the db object
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

            # Fills this list with links to photos
            photos = []
            for medium in favorite.extended_entities['media']:
                if medium['type'] == 'photo' and len(medium['media_url']) > 0:
                    # Prints direct link of images within the tweet
                    photos.append(medium['media_url'])

            # If the tweet is not in the database, process it and reset the counter
            if not search_db(db, tweetID):
                count = 0
                for photo in photos:
                    count += 1

                    # Download the image from the link, using the provided naming scheme
                    success = download_image(photo,[author,tweetID,str(count)], User)
                    if success == 'Y':
                        goodDL += 1
                    else:
                        badDL += 1

                    # Add the tweet to the database
                    write_db(rowsAppend, tweetID, author, date, tweetLink, photo, count, success)
                    prevLoggedCount = 0

            # If it is in the database, increment the counter
            else:
                prevLoggedCount += 1

            # If there were 20 previously logged posts in a row, stop processing
            if prevLoggedCount > 20:
                break
            
            print('\r'+str(tweetCount),end='')



    # Add the new entries to the database
    db = db.append(rowsAppend)

    # Sort the database by twitter ID
    db.sort_values(by=['tweetID'])
    print('\n\n')
    print(db.head(1000000))

    # Save the database
    db.to_excel('twitDB.xlsx', index=False)

    # Using Openpyxl to convert plaintext to hyperlinks
    create_hyperlinks()

    print(f'Successfully downloaded {goodDL} images.\nFailed to download {badDL} images.')


# Function to populate the excel file with twitter data from new tweets
def write_db(rowsAppend, tweetID, author, date, tweetLink, photo, count, success):
    rowsAppend.append({'tweetID': tweetID, 'author': author, 'date': date,
                           'link': tweetLink, 'imageLink': photo, 'count': count, 'success': success})


# Function to search Excel to see if the tweet already exists in the database
def search_db(db, tweetID):
    return tweetID in set(db["tweetID"])

# Function to remove hyperlink formating with regex
def remove_hyperlinks():
    wb = openpyxl.load_workbook('twitDB.xlsx')
    sheet = wb.active

    hyperlinkRE = re.compile(r'\("(.*)",')
    for cell in list(sheet.columns)[3]:
        linkSearch = hyperlinkRE.search(cell.value)
        if linkSearch is not None:
            cell.value = linkSearch[1]

    for cell in list(sheet.columns)[4]:
        linkSearch = hyperlinkRE.search(cell.value)
        if linkSearch is not None:
            cell.value = linkSearch[1]

    wb.save('twitDB.xlsx')
    wb.close()


# Function to add hyperlink formatting
def create_hyperlinks():
    wb = openpyxl.load_workbook('twitDB.xlsx')
    sheet = wb.active

    # If the cell is not formatted as a hyperlink, do so
    for cell in list(sheet.columns)[3]:
        if cell.value[0] != '=':
            cell.value = '=HYPERLINK("{}", "{}")'.format(cell.value, cell.value)
    for cell in list(sheet.columns)[4]:
        if cell.value[0] != '=':
            cell.value = '=HYPERLINK("{}", "{}")'.format(cell.value, cell.value)


    wb.save('twitDB.xlsx')
    wb.close()


# Function to download and save images
def download_image(link, nameList, User):
    name = '-'.join(nameList)
    p = f'C:\\Users\\edbry\\Pictures\\TwitterDL\\{User}\\'
    if not os.path.isdir(p):
        os.makedirs(p)
    res = requests.get(link)
    try:
        res.raise_for_status()
    except:
        print(f'\nFailed to download: {link}\n')
        return 'N'
    imageFile = open(f'C:\\Users\\edbry\\Pictures\\TwitterDL\\{User}\\{name}{link[-4:]}', 'wb')
    for chunk in res.iter_content(100000):
        imageFile.write(chunk)
    imageFile.close()

    return 'Y'


if __name__ == "__main__":
    main()
