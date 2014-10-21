# Előadók klaszterezése közösségi zenei adatbázisokban

## Adatgyűjtés

### 1.) Használt lekérdezések
A Last.fm API-jából két lekérdezést fogunk használni. A **[user.GetTopArtists](http://www.last.fm/api/show/user.getTopArtists)** és az **[artist.GetTopTags](http://www.last.fm/api/show/artist.getTopTags)** lekérdezéseket.

#### Top előadók lekérdezése
Illusztráció:
```json
{
    "toptags": {
        "tag": [
            {
                "name": "pop",
                "count": "100",
                "url": "http://www.last.fm/tag/pop"
            },
            {
                "name": "female vocalists",
                "count": "72",
                "url": "http://www.last.fm/tag/female%20vocalists"
            },
```

A JSON-ben a top level adatszerkezet egy objektum (jelölése: {}).
Ennek a 'topartists' mezőben található 'artist' mezőben található lista az, ami nekünk kell.
A listában objektumok vannak, mindegyik objektum az előadóról tárol információkat. Nekünk csak a 'name' mező értéke fontos.

#### Top tag-ek lekérdezése
blabla

### 2.) Adat tárolása

#### Adatbázis séma
blabla

