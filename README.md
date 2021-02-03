# youtube-playlist-copier
Python script for cloning any YouTube playlist into a custom playlist.

## TODO:
- Fix 500 errors in API method
- ~~Add logic to do a diff and only update newly added videos~~
- Automate using CI/CD

### Bonus:
Postman collection to handle very large playlists:
https://www.getpostman.com/collections/ade346447f434f49cde5


```javascript
// Run this JS snippet on a playlist page to extract the video ids:
var elms = document.querySelectorAll("[id='video-title']");
var expr = /\?v=(.+)&list/;
var vids = [];
for(var i = 0; i < elms.length; i++) 
        vids.push(expr.exec(elms[i].href)[1]);
console.log(vids)
```
