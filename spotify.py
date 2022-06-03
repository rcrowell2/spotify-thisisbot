import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
import math
import datetime as dt
'''
 simple command line application I made to update a playlist I make using
 the spotify generated "This is (Artist)" playlists
 
 Checks for duplicate songs and pulls in values from list.txt file now
 but can uncomment a block of code and will just pull users top 20 artists
'''


# fidns the "This is XXXX" playlistID for a given artist and returns it
def findPlaylist(sp, artist):
    searchTerm = 'This is {name}'.format(name=artist)
    print 'Searching for: %s' % searchTerm
    thisIs = sp.search(searchTerm, limit=1, type='playlist')
    playlistID = thisIs['playlists']['items'][0]['id']
    print 'Playlist ID Found: %s' % playlistID
    return playlistID

# adds trackID's to the songlist passed
def getSongsFromPlaylist(sp, playlistID, songList):
    songs = sp.playlist(playlistID)
    #add all track id's to a list
    for i, track in enumerate(songs['tracks']['items']):
        
        if track['track'] is not None and track['track']['id'] is not None:
            print("\tAdded: %s to the track list" % (track['track']['name']))
            songList.append(track['track']['id'])

# adds the given songlist to the given playlist
def addSongsToPlaylist(sp, playlistID, songList):
    #get test songlist
    oldSongs = []
    print 'GATHERING OLD SONGS'
    getSongsFromPlaylist(sp, playlistID, oldSongs)

    songsToAdd = list(set(songList + oldSongs))
    while '' in songsToAdd:
        songsToAdd.remove('')

    playlistLength = len(songsToAdd)
    if playlistLength > 100:
        numRuns = math.ceil(playlistLength / 100.0)
        for n in range(int(numRuns)):
            #if the first value submit first hundred
            if n == 0:
                sp.playlist_replace_items(playlistID, songsToAdd[0:100])
            else:
                sp.playlist_add_items(playlistID, songsToAdd[(100*n):(100*(n+1))])

    else:
        sp.playlist_replace_items(playlistID, songsToAdd)

    #insert in batches
    print 'Added %d songs to the playlist' % playlistLength

def readFile(filename):
    nameList = []
    with open(filename) as f:
        nameList = f.readlines()
    return nameList

def main():
    os.environ["SPOTIPY_CLIENT_ID"] = 'PUT_CLIENT_ID_HERE'
    os.environ["SPOTIPY_CLIENT_SECRET"] = 'PUT_CLIENT_SECRET_HERE'
    os.environ["SPOTIPY_REDIRECT_URI"] = 'http://localhost/'
    
    scope = 'playlist-modify-public user-top-read'

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    
    nameList = []
    songList = ['']
        
    # this block would take the current users top 20 artists and create the playlist that way
#    topArtists = sp.current_user_top_artists()
#    for artist in topArtists['items']:
#        nameList.append(artist['name'])

    # current way is to read in the list from text file
    nameList = readFile('list.txt')
    
    for name in nameList:
        playlistID = findPlaylist(sp, name)
        getSongsFromPlaylist(sp, playlistID, songList)

    test_id = 0
    user_playlists = sp.current_user_playlists(limit=1)
    #print user_playlists
    for playlist in user_playlists['items']:
        print playlist['name']
        if playlist['name'] == 'test':
            test_id = playlist['id']
            break
    print 'Playlist ID found: %s' % test_id
    
    # need to add a check to see if songs already in the playlist before i add
    # doesn't duplicate check
    addSongsToPlaylist(sp, test_id, songList)
    
    
    now = dt.datetime.now()
    newDesc = 'Last updated at {day}'.format(day=now)
    print newDesc
    sp.playlist_change_details(test_id, description=newDesc)

main()
