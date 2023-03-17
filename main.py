from urllib.request import urlopen
import json

# json brany z url https://www.reddit.com/r/Showerthoughts/top/.json?t=all&limit=2

# Open json from file posts.json
postsJson = json.load(open('posts.json'))
# foreach post in postsJson
for post in postsJson['data']['children']:
    print(post['data']['title'])
    # post content
    print(post['data']['selftext'])