# A JSON deszerializálását, és python-os adatszerkezetekké alakítását végzi.
import json

# Az URL összeállásításhoz a paraméterek helyes konverzióját végzi (például egy előadó,
# akinek a nevében van szóköz, azt kicseréli %20-ra)
import urllib

# A HTTP lekéréseket végző HTTP kliens.
import httplib2

# Adatbázis model
import model


# --------------- Globális változók a kényelem érdekében

# default Last.fm usernév (user-ek, akiknek az adataival dolgozunk: molnarmarcell, csorvagep, Cangooroo)
USER = 'Cangooroo'

BASE_URL = 'http://ws.audioscrobbler.com/2.0/'
API_KEY = '39431f9f072f751be8f9477ba1411442'
FORMAT = 'json'
LIMIT = 6

# ---------------

# --------------- Segéd függvények

def construct_url(parameters, base_url=BASE_URL):
    """
    Összeállítja az URL-t, a GET lekérdezéshez a base URL-ből és a paraméterekből.
    """
    return '{base_url}?{parameters}'.format(base_url=BASE_URL, parameters=parameters)


def get_topartists(http_client, user=USER, api_key=API_KEY, format=FORMAT, limit=LIMIT):
    """
    Lekérdezi a megadott user-től a top előadók listáját
    """

    # Beállítjuk a lekérdezés paramétereit
    request_parameters = urllib.parse.urlencode({
        'method': 'user.gettopartists',
        'user': user,
        'api_key': api_key,
        'format': format,
        'limit': limit
    })

    # Elvégezzük a lekérdezést. A visszakapott adatok a content-ben lesznek
    response, content = http_client.request(construct_url(request_parameters), 'GET')

    # A JSON-ben a top level adatszerkezet egy objektum (jelölése: {}).
    # Ennek a 'topartists' mezőben található 'artist' mezőben található lista az, ami nekünk kell.
    # A listában objektumok vannak, mindegyik objektum az előadóról tárol információkat. Nekünk csak
    # a 'name' mező értéke fontos.
    #
    # Illusztráció (a JSON eleje hasonlóan néz ki):
    #
    # {
    # "topartists": {
    # "artist": [
    #         {
    #             "name": "Pendulum",
    #             "playcount": "11",
    #             "mbid": "2030e776-73b2-4cf8-8c15-813e801f8151",
    #             "url": "http:\/\/www.last.fm\/music\/Pendulum",
    #             "streamable": "0",
    #               ...
    #               ...
    #               ...
    #
    artists = [artist.get('name') for artist in json.loads(content.decode()).get('topartists').get('artist')]

    # Az artists változóban tehát egy lista lesz, amiben a top előadók nevei találhatóak.
    # Ez a lista a visszatérési értékünk
    return artists


def get_toptags(http_client, artist, api_key=API_KEY, format=FORMAT):
    """
    A paraméterben megadott előadó top tag-jeit kérdezi le.
    """

    # Beállítjuk a lekérdezés paramétereit
    request_parameters = urllib.parse.urlencode({
        'method': 'artist.gettoptags',
        'artist': artist,
        'api_key': api_key,
        'format': format
    })

    # Elvégezzük a lekérdezést. A visszakapott adatok a content-ben lesznek
    response, content = http_client.request(construct_url(request_parameters), 'GET')

    # A JSON-ben a top level adatszerkezet egy objektum (jelölése: {}).
    # Ennek a 'toptags' paraméterében található 'tag' paraméterben található lista az, ami nekünk kell.
    # Ebben a listában objektumok találhatók (Egy objektum egy tag adatait tartalmazza). Mindegyik objektumból nekünk
    # a 'name' és a 'count' mezők értékére van szükség.
    #
    # Ezeket a name-count értékeket páronként a toptags listában tároljuk el.
    #
    #
    # Illusztráció (a JSON eleje hasonlóan néz ki):
    #
    # {
    # "toptags": {
    # "tag": [
    #         {
    #             "name": "Drum and bass",
    #             "count": "100",
    #             "url": "http://www.last.fm/tag/drum%20and%20bass"
    #         },
    #         {
    #             "name": "liquid funk",
    #             "count": "47",
    #             "url": "http://www.last.fm/tag/liquid%20funk"
    #         },
    #       ...
    #       ...
    #       ...
    try:
        toptags = [(tag.get('name'), tag.get('count')) for tag in
                   json.loads(content.decode()).get('toptags').get('tag')]
    except Exception:
        # Exception általában abból adódik, hogy az előadónév nem jó (például Valaki ft. Valaki), ilyenkor pedig
        # a Last-fm adatbázisában nincs hozzá adat, a szerver nem tölti ki a megfelelő mezőket a json-ben, amikre
        # nem tudunk hivatkozni, így Exception-t kapunk. Ilyenkor tehát üres a tag-ek listája.
        return []
    else:
        # Ha nem történt exception, akkor visszatérünk a (tag, count) párosok listájával.
        return toptags


# ------------------
# ------------------ Segédfüggvények az adatok elmentéséhez

def save_artists(artists, session):
    for artist in artists:
        new_artist = model.Artist(name=artist)
        if session.query(model.Artist.id).filter(model.Artist.name == new_artist.name).count() > 0:
            pass
        else:
            session.add(new_artist)


def save_tags(artist_name, tags, session):
    artist = session.query(model.Artist.id).filter(model.Artist.name == artist_name).first()

    for tag, count in tags:
        new_tag = model.Tag(name=tag, count=count, artist_id=artist.id)
        if session.query(model.Tag.id).filter(model.Tag.name == new_tag.name,
                                              model.Tag.artist_id == new_tag.artist_id).count() > 0:
            pass
        else:
            session.add(new_tag)

# -------------- Fő program
if __name__ == '__main__':

    # Az SQLite adatbázishoz szükséges modulok
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///tags.sqlite')
    session = sessionmaker()
    session.configure(bind=engine)
    model.Base.metadata.create_all(engine)
    s = session()

    # HTTP kliens példányosítása (a .cache könyvtárba cash-el)
    http_client = httplib2.Http('.cache')

    # Top előadók lekérdezése
    artists = get_topartists(http_client)

    # Előadók elmentése az adatbázisba
    save_artists(artists, s)

    for artist in artists:
        print(artist, end=': ')
        tags = get_toptags(http_client, artist)  # Előadónként top tag-ek lekérdezése
        save_tags(artist, tags, s)
        print(tags)

    s.commit()