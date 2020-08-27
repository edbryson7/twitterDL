import twitKeys as tk
import tweepy

auth = tweepy.OAuthHandler(tk.API_KEY, tk.API_SECRET)
api = tweepy.API(auth)



count=0
# This variable hold the username or the userid of the user you want to get favorites from
# This needs to be the users unique username 
User = "@edzbrys"
# Cursor is the search method this search query will return 20 of the users latest favourites just like the php api you referenced
for favorite in tweepy.Cursor(api.favorites, id=User).items(2000):
    # To get diffrent data from the tweet do "favourite" followed by the information you want the response is the same as the api you refrenced too

    #Basic information about the user who created the tweet that was favorited
    # Print the screen name of the tweets auther
    print('\n\n\nTweet Author:'+str(favorite.user.screen_name.encode("utf-8")))
    #print('Name: '+str(favorite.user.name.encode("utf-8")))


    #Basic information about the tweet that was favorited
    print('\nTweet:')
    # Print the id of the tweet the user favorited
    print('Tweet Id: '+str(favorite.id))
    # Print the text of the tweet the user favorited
    print('Tweet Text: '+str(favorite.text.encode("utf-8")))
    # Encoding in utf-8 is a good practice when using data from twitter that users can submit (it avoids the program crashing because it can not encode characters like emojis)
    try:
        print(['No Image', 'Image'][True in [medium['type'] == 'photo' for medium in favorite.entities['media']]])
    except:
        print("No picture in this tweet")
    count+=1
    print(count)