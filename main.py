import os
import sys
import json
import datetime
import google_auth_oauthlib.flow
import google.oauth2.credentials
import google.auth.transport
import googleapiclient.discovery
# import webbrowser
# from urllib.request import urlopen
from urllib.parse import parse_qs, urlparse

API_KEY = "AIzaSyCrf3ID5N_1B1nrj9Xh82zUlZvRmw1wk44"
CLIENT_SECRETS_FILE = "credentials/credentials.json"
scopes = ["https://www.googleapis.com/auth/youtube"
          ]  # this is the min required scope

# defaults
url_source = 'https://www.youtube.com/playlist?list=UUMOB6uDg7e-h8OuCw8dK2_Q'  # source playlist url
url_dest = 'https://www.youtube.com/playlist?list=PLWFhH0ThGhhxLEMwRqmFSsD0FD4ix1hjs'  # destination playlist url
use_pos = False

# from config
try:
	args = sys.argv
	with open(f'config/{args[1]}.json', 'r') as fp:
		config = json.loads(fp.read())
		# print(config)
		url_source = config['url_source']
		url_dest = config['url_dest']
		if 'use_pos' in config: use_pos = bool(config['use_pos'])
		print("using config: ", args[1])
except Exception as e:
	print(e, "using defaults")

# STEP 1: EXTRACT VIDEO LINKS FROM PLAYLIST:

# extract playlist id from url
query = parse_qs(urlparse(url_source).query, keep_blank_values=True)
playlist_id = query["list"][0]

query = parse_qs(urlparse(url_dest).query, keep_blank_values=True)
playlist_id_dest = query["list"][0]

# OAuth2 flow
creds = ""
try:
	with open('temp/credentials_dump.json', 'r') as fp:
		creds = json.loads(fp.read())
except Exception as e:
	print(e)

print(creds)
# exit(0)

if not creds:
	print("initial flow")
	flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
	    CLIENT_SECRETS_FILE, scopes)
	credentials = flow.run_console()
else:
	print("refresh flow")
	credentials = google.oauth2.credentials.Credentials(
	    creds['token'],
	    refresh_token=creds['refresh_token'],
	    id_token=creds['id_token'],
	    token_uri=creds['token_uri'],
	    client_id=creds['client_id'],
	    client_secret=creds['client_secret'],
	    scopes=creds['scopes'],
	)
	expiry = creds['expiry']
	expiry_datetime = datetime.datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')
	credentials.expiry = expiry_datetime
	# refresh token
	request = google.auth.transport.requests.Request()
	if credentials.expired:
		try:
			credentials.refresh(request)
		except Exception as e:
			print(e)
			print("deleting stored credentials and exiting...")
			os.remove('temp/credentials_dump.json')
			exit(1)

# formatting and saving credentials
creds = {
    'token': credentials.token,
    'refresh_token': credentials.refresh_token,
    'id_token': credentials.id_token,
    'token_uri': credentials.token_uri,
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'scopes': credentials.scopes,
    'expiry': datetime.datetime.strftime(credentials.expiry,
                                         '%Y-%m-%d %H:%M:%S')
}
with open('temp/credentials_dump.json', 'w') as fp:
	json.dump(creds, fp)

print(f'get all playlist items links from {playlist_id}')
youtube = googleapiclient.discovery.build("youtube",
                                          "v3",
                                          developerKey=API_KEY,
                                          credentials=credentials)


def get_playlist_items(playlist_id, youtube):
	request = youtube.playlistItems().list(part="snippet",
	                                       playlistId=playlist_id,
	                                       maxResults=1000)
	response = request.execute()

	playlist_items = []  # will be a list of dicts
	while request is not None:
		response = request.execute()
		playlist_items += response["items"]
		request = youtube.playlistItems().list_next(request, response)

	return playlist_items


playlist_items_source = get_playlist_items(playlist_id, youtube)
playlist_items_dest = get_playlist_items(playlist_id_dest, youtube)

videoIdsSource = [
    t["snippet"]["resourceId"]["videoId"] for t in playlist_items_source
]

videoIdsDest = [
    t["snippet"]["resourceId"]["videoId"] for t in playlist_items_dest
]

# only clone missing items
videoIds = [
    videoId for videoId in videoIdsSource if videoId not in videoIdsDest
]

urls = [
    f'https://www.youtube.com/watch?v={t}&list={playlist_id}&t=0s'
    for t in videoIds
]

print(f"total: {len(urls)}")
print(urls)

# make it chronological (optional)
videoIds.reverse()
print(videoIds, len(videoIds))

# STEP 2: CREATE NEW PLAYLIST FROM EXTRACTED VIDEOS:
'''
API FLOW (Only usable for small playlist or playlist updates)
'''
# extract playlist id from url
query = parse_qs(urlparse(url_dest).query, keep_blank_values=True)
playlist_id = query["list"][0]
print(playlist_id)


def response_callback(request_id, response, exception):
	if exception is not None:
		print(request_id, exception)
		pass
	else:
		print(request_id, response)
		pass


# chunking to handle 1000 call batch limit
n = 1000
videoIdsChunked = [videoIds[i:i + n] for i in range(0, len(videoIds), n)]
print("No. of chunks: ", len(videoIdsChunked))

# batch add videos to playlist (batch limit = 1000 calls)
batch = youtube.new_batch_http_request()
pos = 0
for videoIdChunk in videoIdsChunked:
	for videoId in videoIdChunk:
		batch.add(
		    youtube.playlistItems().insert(
		        part="snippet",
		        body={
		            "snippet": {
		                "playlistId": playlist_id,  # an actual playlistid
		                "position": [None, pos][use_pos],
		                "resourceId": {
		                    "kind": "youtube#video",
		                    "videoId": videoId
		                }
		            }
		        }),
		    callback=response_callback)
		# print(pos)
		pos = pos + 1
	print("Batch length: ", len(videoIdChunk))
	responses = batch.execute()

print("last pos: ", pos)
print("Done!")
''''''
'''
MANUAL FLOW (uncomment imports!)
'''
# videoLinks = videoIds # a ghost of broken code past

# # trying to avoid error 413 - request is too large by chunking up the list
# n = 50 # size of chunk (youtube playlist limit is 50)
# videoLinksChunked = [videoLinks[i:i + n] for i in range(0, len(videoLinks), n)]

# print(videoLinksChunked)

# playListURLs = []

# for videoLinksChunk in videoLinksChunked:
# 	listOfVideos = "http://www.youtube.com/watch_videos?video_ids=" + ','.join(videoLinksChunk)
# 	print(listOfVideos)

# 	response = urlopen(listOfVideos)
# 	playListLink = response.geturl()
# 	print(playListLink)

# 	playListLink = playListLink.split('list=')[1]
# 	print(playListLink)

# 	# open newly created playlist (only works if script is run manually)
# 	playListURL = "https://www.youtube.com/playlist?list="+playListLink+"&disable_polymer=true"
# 	webbrowser.open(playListURL)

# 	playListURLs.append(playListURL)

# print("Playlists: ")
# print(playListURLs) # merge these after opening them individually
''''''
