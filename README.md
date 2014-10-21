# Előadók klaszterezése közösségi zenei adatbázisokban

## Adatgyűjtés

### 1.) Használt lekérdezések
A Last.fm API-jából két lekérdezést fogunk használni. A **[user.GetTopArtists](http://www.last.fm/api/show/user.getTopArtists)** és az **[artist.GetTopTags](http://www.last.fm/api/show/artist.getTopTags)** lekérdezéseket.

#### Top előadók lekérdezése
Illusztráció (részlet a JSON elejéből):
```json
{
    "topartists": {
        "artist": [
            {
                "name": "Dream Theater",
                "playcount": "1849",
                "mbid": "28503ab7-8bf2-4666-a7bd-2644bfc7cb1d",
                "url": "http://www.last.fm/music/Dream+Theater",
                "streamable": "0",
                "image": [
                    {
                        "#text": "http://userserve-ak.last.fm/serve/34/68552548.jpg",
                        "size": "small"
                    },
                ],
                "@attr": {
                    "rank": "1"
                }
            },
            {
                "name": "Dire Straits",
                "playcount": "1592",
                "mbid": "614e3804-7d34-41ba-857f-811bad7c2b7a",
                "url": "http://www.last.fm/music/Dire+Straits",
                "streamable": "0",
                "image": [
                    {
                        "#text": "http://userserve-ak.last.fm/serve/34/12048127.jpg",
                        "size": "small"
                    },
                ],
                "@attr": {
                    "rank": "2"
                }
            },
```

A JSON-ben a top level adatszerkezet egy objektum (jelölése: {}).
A *topartists* mezőben lévő *artist* mezőben lévő listában található előadókból nekünk a **name** mező értékére van szükségünk.

#### Top tag-ek lekérdezése
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
A *toptags* mezőben lévő *tag* listában lévő tag-ekből nekünk a **name** és a **count** mezők értékére van szükségünk.

### 2.) Adat tárolása

#### Adatbázis séma


