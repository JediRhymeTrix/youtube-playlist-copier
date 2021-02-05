# youtube-playlist-copier
Python script for cloning any YouTube playlist into a custom playlist.

#### Automation:
CI/CD tool: https://app.buddy.works/ved914980/youtube-playlist-copier/pipelines \
Scraping tool: https://app.distill.io/watchlist

## TODO:
- ~~Fix 500 errors in API method~~ (will check if it pops up again)
- ~~Add logic to do a diff and only update newly added videos~~
- ~~Automate using CI/CD~~

### Bonus:
Postman collection to handle very large playlists:
https://www.getpostman.com/collections/ade346447f434f49cde5


```javascript
// Run this JS snippet on a playlist page to extract the video ids:
var elms = document.querySelectorAll("[id='video-title']");
var expr = /\?v=(.+)&list/;
var vids = [];
for(var i = 0; i < elms.length; i++) 
       vids.push((expr.exec(elms[i].href) ?? [null, null])[1])
console.log(vids.filter(x => x))
```
