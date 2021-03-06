# A JSON deszerializálását, és python-os adatszerkezetekké alakítását végzi.
import json

# Az URL összeállásításhoz a paraméterek helyes konverzióját végzi (például egy előadó,
# akinek a nevében van szóköz, azt kicseréli %20-ra)
import urllib

# A HTTP lekéréseket végző HTTP kliens.
import httplib2

# Adatbázis model
from numpy.ma.core import _minimum_operation
import model

import numpy as np

from scipy.cluster.vq import kmeans, kmeans2, vq

import random

import copy

from scipy.cluster.hierarchy import linkage, dendrogram

from scipy.spatial.distance import pdist


from matplotlib.pyplot import show

# --------------- Globális változók a kényelem érdekében

# default Last.fm usernév (user-ek, akiknek az adataival dolgozunk: molnarmarcell, csorvagep, Cangooroo)
USERS = ['csorvagep', 'Cangooroo']

BASE_URL = 'http://ws.audioscrobbler.com/2.0/'
API_KEY = '39431f9f072f751be8f9477ba1411442'
FORMAT = 'json'
LIMIT = 200

# ---------------

# --------------- Segéd függvények

def construct_url(parameters, base_url=BASE_URL):
    """
    Összeállítja az URL-t, a GET lekérdezéshez a base URL-ből és a paraméterekből.
    """
    return '{base_url}?{parameters}'.format(base_url=BASE_URL, parameters=parameters)


def get_topartists(http_client, api_key=API_KEY, format=FORMAT, limit=LIMIT, user=''):
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
        toptags = []
        for tag in json.loads(content.decode()).get('toptags').get('tag'):
            name = tag.get('name').upper()

            if(name in ['DNB', "DRUM'N'BASS", 'DRUM & BASS', 'DRUM N BASS',
                        'LIQUID', 'LIQUID DRUM AND BASS', 'LIQUID FUNK']):
                name = 'DRUM AND BASS'

            if(name in ['PUNK', 'PUNK ROCK', 'POP PUNK', 'EMO']):
                name = 'PUNK'

            if(name in ['HIP HOP', 'UNDERGROUND HIP-HOP', 'JAZZ HOP', 'INSTRUMENTAL HIP-HOP'
                        'TRIP-HOP', 'GLITCH', 'GLITCH HOP', 'GLITCH-HOP', 'AUSSIE HIP HOP']):
                name = 'HIP-HOP'

            if(name in ['GANGSTA', 'GANGSTA RAP', 'WEST COAST RAP', 'RAPCORE']):
                name = 'RAP'

            if(name in ['R&B', ]):
                name = 'RNB'

            if(name in ['NEUROFUNK', ]):
                name = 'FUNK'

            if(name in ['ELECTRONICA', ]):
                name = 'ELECTRONIC'

            if(name in ['ALTERNATIVE ROCK', 'ALTERNATIVE', 'INDIE ROCK', 'HARD ROCK',
                        'CLASSIC ROCK', 'NU METAL']):
                name = 'ROCK'

            if(name in ['CHILLSTEP', ]):
                name = 'DUBSTEP'

            if int(tag.get('count')) > 50:
                toptags.append((name, tag.get('count')))
                print('{}({})'.format(name, tag.get('count')), end=', ')

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


def create_vectors(artist, session):
    tags = session.query(model.Tag).filter(model.Tag.artist_id == artist.id)

    ds = [
        'DRUM AND BASS',
        'ROCK',
        'PUNK',
        'HIP-HOP',
        'RAP',
        'DUBSTEP',
        'ELECTRONIC',
        'INDIE',
        'SOUL',
        'POP',
        'RNB',
        'FUNK',
        ]

    printit = False

    if tags.count()>0:
        for tag in tags:
            if tag.name in ds:
                printit = True

    if printit:
        print(artist.name,end=': ')
        artist_vector = model.ArtistVector(artist_id=artist.id)
        artist_vector.drum_and_bass = 0
        artist_vector.rock = 0
        artist_vector.punk = 0
        artist_vector.hip_hop = 0
        artist_vector.rap = 0
        artist_vector.dubstep = 0
        artist_vector.electronic = 0
        artist_vector.indie = 0
        artist_vector.soul = 0
        artist_vector.pop = 0
        artist_vector.rnb = 0
        artist_vector.funk = 0

        for tag in tags:
            if tag.name in ds:
                print(tag.name, end=', ')
                if tag.name == 'DRUM AND BASS':
                    if artist_vector.drum_and_bass < tag.count:
                        artist_vector.drum_and_bass = tag.count

                if tag.name == 'ROCK':
                    if (artist_vector.rock or 0) < tag.count:
                        artist_vector.rock = tag.count

                if tag.name == 'PUNK':
                    if (artist_vector.punk or 0) < tag.count:
                        artist_vector.punk = tag.count

                if tag.name == 'HIP-HOP':
                    if (artist_vector.hip_hop or 0) < tag.count:
                        artist_vector.hip_hop = tag.count

                if tag.name == 'RAP':
                    if (artist_vector.rap or 0) < tag.count:
                        artist_vector.rap = tag.count

                if tag.name == 'DUBSTEP':
                    if (artist_vector.dubstep or 0) < tag.count:
                        artist_vector.dubstep = tag.count

                if tag.name == 'ELECTRONIC':
                    if (artist_vector.electronic or 0) < tag.count:
                        artist_vector.electronic = tag.count

                if tag.name == 'INDIE':
                    if (artist_vector.indie or 0) < tag.count:
                        artist_vector.indie = tag.count

                if tag.name == 'SOUL':
                    if (artist_vector.soul or 0) < tag.count:
                        artist_vector.soul = tag.count

                if tag.name == 'POP':
                    if (artist_vector.pop or 0) < tag.count:
                        artist_vector.pop = tag.count

                if tag.name == 'RNB':
                    if (artist_vector.rnb or 0) < tag.count:
                        artist_vector.rnb = tag.count

                if tag.name == 'FUNK':
                    if (artist_vector.funk or 0) < tag.count:
                        artist_vector.funk = tag.count
        print()
        session.add(artist_vector)


def compute(session):
        artist_vectors = session.query(model.ArtistVector).all()

        in_raw_data = []

        for artist_vector in artist_vectors:
            row = np.array([
                artist_vector.drum_and_bass,
                artist_vector.rock,
                artist_vector.punk,
                artist_vector.hip_hop,
                artist_vector.rap,
                artist_vector.dubstep,
                artist_vector.electronic,
                artist_vector.indie,
                artist_vector.soul,
                artist_vector.pop,
                artist_vector.rnb,
                artist_vector.nu_metal,
                artist_vector.funk
            ])
            in_raw_data.append(row)

        data = np.vstack(in_raw_data)

        centers, _ = kmeans(data, 26)
        clusters, _ = vq(data, centers)

        # for i, d in enumerate(data):
        #     try:
        #         artist_name = session.query(model.Artist).get(i+1)
        #         print(artist_name.name, d)
        #     except AttributeError:
        #         print(i, d)

        for cluster in range(26):
            for index, cluster2 in enumerate(clusters):
                if cluster2 == cluster:
                    try:
                        artist_vec = session.query(model.ArtistVector).get(index+1)
                        artist_name = session.query(model.Artist).get(artist_vec.artist_id)
                        print(artist_name.name, '-', cluster2)#, '\t\t', data[index])
                    except AttributeError:
                        print(index+1, cluster2)


def distance (v1, v2): #euklideszi távolság számolás két tetszőleges hosszú vektor között, egy számot ad vissza
    distance = 0
    for x in range(0, len(v1)):
        distance += pow(v1[x]-v2[x],2)
    return pow(distance, 0.5)

def weight (vectors): #súlypont számító függvény
    weightpoint = []
    for x in range(0,len(vectors[0])): #csinálunk egy nullás vektort
        weightpoint.append(0.0)
    for x in vectors:
        for y in range(0, len(x)):
            weightpoint[y] = weightpoint[y]+x[y] #összeadjuk az összes koordinátát
    for x in range(0, len(weightpoint)):
        weightpoint[x] = weightpoint[x]/len(vectors) #az összes koordinátát leosztjuk a vektorok számával
    return weightpoint

def kmins (dataset, clusternum): #kmins klaszterező algoritmus
    #inicializálás
    centroids = [] #középvektorokat tartalmazó lista
    clusters = [] #clusterek listája, a dataset elemeit rendezzük majd listákba
    clustersdone = []
    for x in range (0, clusternum): #ahány klasztert szeretnénk annyi random középvektor kell
        clusters.append([]) #hozzáadunk egy új üres listát mindegyik klaszternek

    #középvektorok kiválasztása
    counter = 0
    centroids.append(dataset[0])
    for x in dataset:
        if (not x in centroids) & (distance(weight(centroids),x) > 100): #a középértékeket egymástól megfelelően nagy távolságra választjuk meg, ezzel elkerülhető a 0-ás klaszterek képződése
            centroids.append(x) #mivel véletlenszerű adatok, ezért elvileg bármelyik elem a datasetben megfelelő kezdőpont, feltéve hogy nem egyformák
            counter = counter+1
        if counter==clusternum:
            break
    if counter < clusternum:
        print("Not enough unique data to create {0} clusters.".format(clusternum))
        return []
    else:
        print("Creating {0} clusters.".format(clusternum))

    #klaszterező ciklus
    h=0
    while(h<500):
        for x in range(0, len(dataset)): # az összes dataset beli elemre
            leastindex = 0 #a legkisebb távolságú elem indexe
            leastvalue = 200000.0 #a létező legnagyobb távolság felülbecsülve
            for y in range (0, clusternum): # megnézzük az összes középvektort
                if distance(dataset[x], centroids[y]) < leastvalue: # ha az elem távolsága kisebb az adott vektortól mint bármelyik előzőtől
                    leastvalue = distance(dataset[x], centroids[y]) #eltesszük az új értéket
                    leastindex = y #eltesszük az indexet, minimumkeresés menet közben
            clusters[leastindex].append(dataset[x]) #hozzáadjuk a legközelebbi középvektorral rendelkező klaszterhez az új elemet

        #célteszt
        if len(clustersdone)!=0:
            metric=0
            for x in range(0, clusternum):
                metric = metric+distance(weight(clusters[x]), weight(clustersdone[x])) #ha az előző eredmény távolsága elég kicsi a mostanitól akkor végeztünk
            if metric==0:
                # print("Done, metric seems OK")
                break

        for x in clusters: #elvileg ilyen nem lehet
            if len(x)<1:
                print(h)
                # print("Zero cluster, omitting.")
                return[]

        clustersdone = copy.deepcopy(clusters) #elmentjük a clustert mert be fogjuk piszkolni...
        for x in range(0, clusternum):
            clusters[x].append(centroids[x])
        for x in range(0, clusternum): #az összes clusterhez újraszámoljuk a középvektort
            centroids[x] = weight(clusters[x]) #aztán mehet előlről

        #újrainicializálás
        clusters = []
        for x in range (0, clusternum): #nullázzuk a clusterlistát
            clusters.append([]) #hozzáadunk egy új üres listát mindegyik klaszternek
        h = h+1
    return clustersdone

def hierarhic(dataset, clusternum): #megadjuk neki az adatokat meg hogy kb mennyi klasztert szeretnénk, nyilván a fában nem lesz pont olyan szint
    workingset = []
    for x in range(0, len(dataset)): #inicializálás, a weight függvény miatt kell, mert az kétdimenziós vektor vektorokat eszik
        workingset.append([])
        workingset[x].append(dataset[x])
    while len(workingset)>clusternum: #vágás
        leastdistance = 200000.0
        leastindex1 = 0
        leastindex2 = 1
        for x in range(0,len(workingset)-1): #igen, baromi lassú, nagyon sokszor újragenerálok olyan adatokat amit nem kéne
            for y in range(x+1,len(workingset)): #végignézzük az összeshez az összes többit, kiválasztjuk a elgközelebb levőt
                if(distance(weight(workingset[0]), weight(workingset[x]))<leastdistance):
                    leastindex1=x
                    leastindex2=y
                    leastdistance=distance(weight(workingset[0]), weight(workingset[x]))
        workingset.append(workingset[leastindex1]+workingset[leastindex2]) #eltároljuk az összevont új clustert
        del workingset[leastindex2] #kivesszük a lsitából az összevontakat
        del workingset[leastindex1]
        #print "Number of clusters on this level: {0}".format(len(workingset))
    return workingset

def restoreartists(clusters, expandeddataset): #vissza kéne hozni hogy melyik vektor melyik előadó, erre mondjuk gondolhattam volna hamarabb...
    returnset = []
    for x in range(0, len(clusters)):
        returnset.append([])
    for x in expandeddataset:
        for y in range(0, len(clusters)):
            if x[1] in clusters[y]:
                returnset[y].append(x[0])
    return returnset
#


def compute_own_kmeans(session):
    artist_vectors = session.query(model.ArtistVector).all()

    in_raw_data = []
    in_raw_data2 = []

    for artist_vector in artist_vectors:
        artist_name = session.query(model.Artist).get(artist_vector.artist_id)
        in_raw_data.append([
                artist_vector.drum_and_bass,
                artist_vector.rock,
                artist_vector.punk,
                artist_vector.hip_hop,
                artist_vector.rap,
                artist_vector.dubstep,
                artist_vector.electronic,
                artist_vector.indie,
                artist_vector.soul,
                artist_vector.pop,
                artist_vector.rnb,
                artist_vector.nu_metal,
                artist_vector.funk
            ])

        in_raw_data2.append((artist_name.name, [
                artist_vector.drum_and_bass,
                artist_vector.rock,
                artist_vector.punk,
                artist_vector.hip_hop,
                artist_vector.rap,
                artist_vector.dubstep,
                artist_vector.electronic,
                artist_vector.indie,
                artist_vector.soul,
                artist_vector.pop,
                artist_vector.rnb,
                artist_vector.nu_metal,
                artist_vector.funk
            ]))

    print()

    out = kmins(in_raw_data, 19)

    print(out)
    restored = restoreartists(out, in_raw_data2)

    for cluster_number, cluster in enumerate(restored):
        for artist in cluster:
            print(artist,'-',cluster_number)


def compute_hierarchical(session):
    artist_vectors = session.query(model.ArtistVector).all()

    in_raw_data = []

    for artist_vector in artist_vectors:
        artist_name = session.query(model.Artist).get(artist_vector.artist_id)
        in_raw_data.append([
                artist_vector.drum_and_bass,
                artist_vector.rock,
                artist_vector.punk,
                artist_vector.hip_hop,
                artist_vector.rap,
                artist_vector.dubstep,
                artist_vector.electronic,
                artist_vector.indie,
                artist_vector.soul,
                artist_vector.pop,
                artist_vector.rnb,
                artist_vector.nu_metal,
                artist_vector.funk
            ])

    out = hierarhic(in_raw_data, 19)

    print(out)


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

    for user in USERS:
        # Top előadók lekérdezése
        artists = get_topartists(http_client, user=user)

        # Előadók elmentése az adatbázisba
        save_artists(artists, s)

        for artist in artists:
            print(artist, end=': ')
            tags = get_toptags(http_client, artist)  # Előadónként top tag-ek lekérdezése
            save_tags(artist, tags, s)
            print()
            # print(tags)


    s.commit()

    artists = s.query(model.Artist).all()

    for artist in artists:
        create_vectors(artist, s)

    s.commit()

    print("\n\nA scipy algoritmusa:\n")
    compute(s)

    print("\n\nSaját k-means klaszterezés:\n")
    compute_own_kmeans(s)

    print("\n\nHierarchikus klaszterezés (sokáig tarthat):\n")
    compute_hierarchical(s)

    s.commit()