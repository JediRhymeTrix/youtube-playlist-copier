import google_auth_oauthlib.flow
import googleapiclient.discovery
# import webbrowser
# import numpy as np
# from urllib.request import urlopen
from urllib.parse import parse_qs, urlparse

API_KEY = "AIzaSyCrf3ID5N_1B1nrj9Xh82zUlZvRmw1wk44"
CLIENT_SECRETS_FILE = "credentials.json"
scopes = ["https://www.googleapis.com/auth/youtube"] # this is the min required scope

url_source = 'https://www.youtube.com/playlist?list=UUMOB6uDg7e-h8OuCw8dK2_Q' # source playlist url
url_dest = 'https://www.youtube.com/playlist?list=PLWFhH0ThGhhxLEMwRqmFSsD0FD4ix1hjs' # destination playlist url

# STEP 1: EXTRACT VIDEO LINKS FROM PLAYLIST:

# extract playlist id from url
query = parse_qs(urlparse(url_source).query, keep_blank_values=True)
playlist_id = query["list"][0]

# OAuth2 flow
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes)
credentials = flow.run_console()

print(f'get all playlist items links from {playlist_id}')
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = API_KEY, credentials = credentials)

request = youtube.playlistItems().list(
    part = "snippet",
    playlistId = playlist_id,
    maxResults = 500
)
response = request.execute()

playlist_items = [] # will be a list of dicts
while request is not None:
    response = request.execute()
    playlist_items += response["items"]
    request = youtube.playlistItems().list_next(request, response)

videoIds = [
	t["snippet"]["resourceId"]["videoId"] for t in playlist_items
]

urls = [ 
    f'https://www.youtube.com/watch?v={t}&list={playlist_id}&t=0s'
    for t in videoIds
]

print(f"total: {len(urls)}")
print(urls)

# make it chronological (optional)
videoIds.reverse() 
print(videoIds)

# STEP 2: CREATE NEW PLAYLIST FROM EXTRACTED VIDEOS:

'''
API FLOW
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

# batch add videos to playlist (batch limit = 1000 calls)
batch = youtube.new_batch_http_request()
pos = 0
for videoId in videoIds:
	batch.add(youtube.playlistItems().insert(
			part="snippet",
			body={
				"snippet": {
					"playlistId": playlist_id, #an actual playlistid
					"position": pos,
					"resourceId": {
						"kind": "youtube#video",
						"videoId": videoId
					}
				}
			}
		)
	, callback = response_callback)
	pos = pos + 1
responses = batch.execute()

print("Done!");
''''''

'''
MANUAL FLOW (uncomment imports!)
'''
# videoLinks = []

# for iLine in urls:
# 		if iLine.startswith("https"):
# 				iLine = iLine.rstrip()
# 				# print iLine
# 		if ('v=') in iLine: # https://www.youtube.com/watch?v=aBcDeFGH
# 				iLink = iLine.split('v=')[1]
# 				videoLinks.append(iLink) 
# 		if ('be/') in iLine: # https://youtu.be/aBcDeFGH
# 				iLink =  iLine.split('be/')[1]
# 				videoLinks.append(iLink)

# print(videoLinks)

# # trying to avoid error 413 - request is too large by chunking up the list
# n = 50 # size of chunk (youtube playlist limit is 50)
# videoLinksChunked = [videoLinks[i:i + n] for i in range(0, len(videoLinks), 200)]

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