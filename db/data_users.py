"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
Only for user related database calls
"""

import db.db_connect as dbc
import db.data_playlists as dbp

PLAYLISTS = "playlists"
USERS = "users"

PLNAME = "playlistName"
USERNAME = "userName"

client = dbc.get_client()
if client is None:
    print("FAILED TO CONNECT TO MONGODB")
    exit(1)

OK = 0
NOT_FOUND = 1
DUPLICATE = 2


def get_users():
    """
    returns all users
    """
    return dbc.fetch_all(USERS, USERNAME)


def user_exists(username):
    """
    return true/false whether or not user exists
    """
    rec = dbc.fetch_one(USERS, filters={USERNAME: username})
    return rec is not None


def get_user(username):
    """
    return a user given a username, else NOT_FOUND
    """
    if user_exists(username):
        return dbc.fetch_one(USERS, filters={USERNAME: username})
    else:
        return NOT_FOUND


def add_user(username):
    """
    adds a user, returns whether successful or not
    """
    if user_exists(username):
        return DUPLICATE
    else:
        dbc.insert_doc(USERS, {USERNAME: username,
                               "numFriends": 0,
                               "friends": [],
                               "numPlaylists": 0,
                               "playlists": []
                               })
        return OK


def update_user(user_name, update):
    """
    update an existing user given new data
    """
    if not user_exists(user_name):
        return NOT_FOUND
    else:
        dbc.update_doc(USERS, {USERNAME: user_name}, update)


def del_user(username):
    """
    delete a user by username
    """
    if user_exists(username):
        dbc.del_one(USERS, filters={USERNAME: username})
        return OK
    else:
        return NOT_FOUND


def bef_user(usern1, usern2):
    """
    befriends 2 users by adding each other to their friends list
    also increments their friend count
    """
    update_user(usern2, {"$push": {"friends": usern1}})
    update_user(usern1, {"$push": {"friends": usern2}})
    update_user(usern2, {"$inc": {"numFriends": 1}})
    update_user(usern1, {"$inc": {"numFriends": 1}})


def unf_user(usern1, usern2):
    """
    unfriends 2 users by removing one another from their friends lists
    also decrements their friend count
    """
    update_user(usern2, {"$pull": {"friends": usern1}})
    update_user(usern1, {"$pull": {"friends": usern2}})
    update_user(usern2, {"$inc": {"numFriends": -1}})
    update_user(usern1, {"$inc": {"numFriends": -1}})


def like_playlist(username, playlist_name):
    """
    likes a playlist by adding it to the user's playlists
    also adds the user to the playlist's likes
    """
    dbp.update_playlist(playlist_name, {"$push": {"likes": username}})
    update_user(username, {"$push": {"playlists": playlist_name}})
    update_user(username, {"$inc": {"numPlaylists": 1}})


def unlike_playlist(username, playlist_name):
    """
    unlikes a playlist by removing it from the user's likes
    also removing the user from the playlist's likes
    """
    dbp.update_playlist(playlist_name, {"$pull": {"likes": username}})
    update_user(username, {"$pull": {"playlists": playlist_name}})
    update_user(username, {"$inc": {"numPlaylists": -1}})


def empty():
    """
    empty out the users in the database
    ONLY IF IN TEST_MODE
    """
    dbc.del_many(USERS)
