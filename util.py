import json
import logging
import os
import random
from time import sleep
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
import musicbrainzngs as mbz
import pandas as pd
from thefuzz import fuzz
from requests.exceptions import ReadTimeout
from slugify import slugify
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

mbz.set_useragent(
    os.environ.get("MUSICBRAINZ_APP_NAME", "music-miner"),
    os.environ.get("MUSICBRAINZ_APP_VERSION", "0.1.2"),
    os.environ.get("MUSICBRAINZ_APP_ADDRESS", ""))

spotify = Spotify(client_credentials_manager=SpotifyClientCredentials(),
                  requests_timeout=10, retries=3)


@dataclass
class MusicBrainzArtistCredits:
    mbids: List[str]
    names: List[str]
    credit: str

    @property
    def count(self):
        return len(self.names)

    def __iter__(self):
        return iter(zip(self.mbids, self.names))

    @classmethod
    def from_dict(cls, item):
        mbids = [ac["artist"]["id"] for ac in item["artist-credit"]
                 if isinstance(ac, dict)]
        names = [ac["artist"]["name"] for ac in item["artist-credit"]
                 if isinstance(ac, dict)]

        if "artist-credit-phrase" in item \
                and len(item["artist-credit-phrase"]) > 0:
            credit = item["artist-credit-phrase"]
        elif all(isinstance(ac, dict) for ac in item["artist-credit"]):
            credit = ", ".join(ac["artist"]["name"]
                             for ac in item["artist-credit"])
        else:
            credit = " ".join(ac["artist"]["name"]
                              if isinstance(ac, dict) else ac
                              for ac in item["artist-credit"])
        return cls(mbids=mbids, names=names, credit=credit)


def fetch_album_chart_by_month():
    """Chart 2000 - 2021: the top 50 chart for every month from Jan 2000 to Jun 2021
    Note: song and albums ranked weekly by indicative revenue globally over a certain period. Indicative Revenue is a model for global sales volume, adjusted for inflation and currency exchange, and using IFPI estimated annual revenue for the recorded music industry in each country.
    #albums_chart_by_month = pd.read_csv("https://chart2000.com/data/chart2000-albummonth-0-3-0063.csv")
    """
    return pd.read_csv("/Users/pez/Downloads/chart2000-songmonth-0-3-0063.csv")


def fetch_song_chart_by_month():
    """Chart 2000 - 2021: the top 50 chart for every month from Jan 2000 to Jun 2021
    Note: song and albums ranked weekly by indicative revenue globally over a certain period. Indicative Revenue is a model for global sales volume, adjusted for inflation and currency exchange, and using IFPI estimated annual revenue for the recorded music industry in each country.
    #songs_chart_by_month = pd.read_csv("https://chart2000.com/data/chart2000-songmonth-0-3-0063.csv")
    """
    return pd.read_csv("/Users/pez/Downloads/chart2000-albummonth-0-3-0063.csv")


def fetch_spotify_chart(num_samples=1000, seed=42):
    # @TODO: series of fetching for random date from 1/1/2017 to present day.
    # currently: batshit crazy 4.3 GB spotify top200 chart CSV from kaggle
    # https://www.kaggle.com/general/232036
    # url = "https://spotifycharts.com/regional/global/weekly/2018-10-12--2018-10-19/download"
    random.seed(seed)
    filename = "/Users/pez/Downloads/charts.csv"
    n = sum(1 for line in open(filename)) - 1  # number of records in file (excludes header)
    s = num_samples  # desired sample size
    skip = sorted(random.sample(range(1, n + 1), n - s))  # the 0-indexed header will not be included in the skip list
    df = pd.read_csv(filename, skiprows=skip)
    df["id"] = df["url"].apply(lambda url: url.split("/")[-1])
    return df


# def fetch_spotify_chart(date):
#    charts = []
#    for month in range(1, 12):
#        df = pd.read_csv(f"https://spotifycharts.com/regional/global/daily/2017-{month:2d}-01/download")
#        charts.append(df)


def filter_by_artist(artist_key="artist"):
    def _f(df, artist):
        return df[artist_key] == artist
    return _f


def filter_by_album(artist_key="artist", album_key="album"):
    def _f(df, artist, album):
        return (df[artist_key] == artist) & (df[album_key] == album)
    return _f


def filter_by_track(artist_key="artist", track_key="song"):
    def _f(df, artist, track):
        return (df[artist_key] == artist) & (df[track_key] == track)
    return _f


def resolve_names(artist, track):
    result = mbz.search_recordings(f"artist:{artist} recording:{track}", limit=1)
    sleep(1)
    try:
        return result["recording-list"][0]["artist-credit"][0]["name"], \
               result["recording-list"][0]["title"]
    except IndexError as err:
        return None


def resolve_release_date(artist_name, track_name):
    release_dates = []
    release_years = []
    # recordings = mbz.search_recordings(f"arid:{artist_mbid} AND recording:\"{track_name}\"")["recording-list"]
    recordings = mbz.search_recordings(f"artist:{artist_name} AND recording:\"{track_name}\"")["recording-list"]
    sleep(1)
    for recording in recordings:
        if "release-list" not in recording:
            continue
        for release in recording["release-list"]:
            if "date" in release:
                if len(release["date"]) == 10:
                    release_dates.append(release["date"])
                    release_years.append(int(release["date"][0:4]))
                elif len(release["date"]) == 4:
                    release_years.append(int(release["date"]))
    release_year = min(release_years) if len(release_years) > 0 else None
    release_date = min(release_dates) if len(release_dates) > 0 else None
    return release_year, release_date


def best_match(result, artist, track):
    for t in result["tracks"]["items"]:
        t_artist = t["artists"][0]["name"]
        t_track = t["name"]
        artist_fuzz_score = fuzz.token_sort_ratio(artist, t_artist)
        track_fuzz_score = fuzz.token_sort_ratio(track, t_track)
        if artist_fuzz_score > 85 and track_fuzz_score > 85:
            return t
    return None


def fetch_track(artist, track):
    artists = [artist]
    if artist.startswith("The "):
        artists.append(artist[4:])
    for artist in artists:
        try:
            artist_ = artist
            result = spotify.search(f"track:{track} artist:{artist}")
            sleep(.25)
            best_match_ = best_match(result, artist, track)
            if result["tracks"]["total"] == 0 and not best_match_:
                artist_, _ = resolve_names(artist, track)
                result = spotify.search(f"track:{track} artist:{artist_}")
                best_match_ = best_match(result, artist, track)
                sleep(.25)
            if result["tracks"]["total"] == 0 and not best_match_:
                result = spotify.search(f"{artist} {track}")
                best_match_ = best_match(result, artist, track)
                sleep(.25)
            if result["tracks"]["total"] == 0 and not best_match_:
                result = spotify.search(f"{artist_} {track}")
                best_match_ = best_match(result, artist, track)
                sleep(.25)
            if result["tracks"]["total"] == 0 and not best_match_:
                return None
        except ReadTimeout:
            print("spotify time out.")
            return None
        if best_match_:
            return best_match_
    return None


def fetch_track_audio_features(track_id):
    pass


def with_spotify_track_metadata(df, artist_key="artist", track_key="song"):
    """
    Add Spotify ids and metadata to chart songs.
    Songs that have charted are often on the chart the following week.
    As ids and metadata are added to multiple rows at a time.
    Make sure to skip rows that already have id and metadata.
    """
    for index, record in df.iterrows():
        artist, track = record[artist_key], record[track_key]
        logging.info(f"artist: {artist}, track: {track}")
        filter_by_track_ = filter_by_track(artist_key=artist_key,
                                           track_key=track_key)

        # check if track id is already present
        if "spotify_track_id" in df \
                and len(filter_by_track_(df, artist, track)
                        & (df["spotify_track_id"].isna())) == 0:
            logging.info("skipped: metadata exists")
            continue

        # search for song on spotify
        spotify_track = fetch_track(artist, track)
        if spotify_track is None:
            logging.info(f"skipped: no track found: {artist} - {track}")
            continue

        # add id and metadata to dataframe
        df.loc[filter_by_track_(df, artist, track),
                  "spotify_track_id"] = spotify_track["id"]
        df.loc[filter_by_track_(df, artist, track),
                  "spotify_artist_id"] = spotify_track["artists"][0]["id"]
        df.loc[filter_by_track_(df, artist, track),
                  "spotify_album_id"] = spotify_track["album"]["id"]
        df.loc[filter_by_track_(df, artist, track),
                  "spotify_track_popularity"] = spotify_track["popularity"]
        df.loc[filter_by_track_(df, artist, track),
                  "spotify_track_explicit"] = spotify_track["explicit"]
        df.loc[filter_by_track_(df, artist, track),
                  "spotify_track_duration_ms"] = spotify_track["duration_ms"]
        df.loc[filter_by_track_(df, artist, track),
                  "spotify_track_album_release_date"] = \
            spotify_track["album"]["release_date"]
        df.loc[filter_by_track_(df, artist, track),
                  "spotify_track_album_release_date_precision"] = \
            spotify_track["album"]["release_date_precision"]

        # don't trigger spotify rate-limit
        sleep(1)
        if index % 10 == 0:
            total_tracks = len(df)
            null_tracks = df["spotify_track_id"].isnull().sum()
            print(f"status: {100 - null_tracks / total_tracks * 100:.2f} "
                  f"({total_tracks - null_tracks} / {total_tracks}")
    return df


def fetch_album(artist, album):
    try:
        artist_ = artist
        result = spotify.search(f"album:{album} artist:{artist}")
        if result["tracks"]["total"] == 0:
            artist_, _ = resolve_names(artist, album)
            result = spotify.search(f"track:{album} artist:{artist_}")
            sleep(.25)
        if result["tracks"]["total"] == 0:
            result = spotify.search(f"{artist} {album}")
            sleep(.25)
        if result["tracks"]["total"] == 0:
            result = spotify.search(f"{artist_} {album}")
            sleep(.25)
        if result["tracks"]["total"] == 0:
            return None
    except ReadTimeout:
        print("spotify time out.")
        return None
    return result["tracks"]["items"][0]["album"]


def with_spotify_album_metadata(df, artist_key="artist", album_key="album"):
    """
    Add Spotify ids and metadata to chart songs.
    Songs that have charted are often on the chart the following week.
    As ids and metadata are added to multiple rows at a time.
    Make sure to skip rows that already have id and metadata.
    """
    for index, record in df.iterrows():
        artist, album = record[artist_key], record[album_key]
        logging.info(f"artist: {artist}, album: {album}")
        filter_by_album_ = filter_by_album(artist_key=artist_key,
                                           album_key=album_key)

        # check if track id is already present
        if "spotify_album_id" in df \
                and len(filter_by_album_(df, artist, album)
                        & (df["spotify_album_id"].isna())) == 0:
            logging.info("skipped: metadata exists")
            continue

        # search for song on spotify
        spotify_album = fetch_album(artist, album)
        if spotify_album is None:
            logging.info(f"skipped: no album found: {artist} - {album}")
            continue

        # add id and metadata to dataframe
        df.loc[filter_by_album_(df, artist, album),
               "spotify_album_id"] = spotify_album["id"]
        df.loc[filter_by_album_(df, artist, album),
               "spotify_artist_id"] = spotify_album["artists"][0]["id"]
        df.loc[filter_by_album_(df, artist, album),
               "spotify_total_tracks"] = spotify_album["total_tracks"]
        df.loc[filter_by_album_(df, artist, album),
               "spotify_release_date"] = \
            spotify_album["release_date"]
        df.loc[filter_by_album_(df, artist, album),
               "spotify_release_date_precision"] = \
            spotify_album["release_date_precision"]

        # don't trigger spotify rate-limit
        sleep(1)
        if index % 10 == 0:
            total_albums = len(df)
            null_albums = df["spotify_album_id"].isnull().sum()
            logging.info(f"status: {100 - null_albums / total_albums * 100:.2f} "
                         f"({total_albums - null_albums} / {total_albums}")
    return df


def fetch_artist(artist):
    try:
        result = spotify.search(f"artist:{artist}")
        sleep(.25)
        if result["tracks"]["total"] == 0:
            return None
    except ReadTimeout:
        print("spotify time out.")
        return None
    return result["tracks"]["items"][0]


def with_spotify_artist_metadata(df, artist_key="artist"):
    """
    Add Spotify ids and metadata to dataframe with artist data
    As ids and metadata are added to multiple rows at a time.
    Make sure to skip rows that already have id and metadata.
    """
    for index, record in df.iterrows():
        artist = record[artist_key]
        logging.info(f"artist: {artist}")
        filter_by_artist_ = filter_by_artist(artist_key=artist_key)

        # check if artist id is already present
        if "spotify_artist_id" in df \
                and len(df[(filter_by_artist_(df, artist))
                           & (df["spotify_artist_id"].isna())]) == 0:
            logging.info("skipped: metadata exists")
            continue

        # search for artist on spotify
        spotify_artist = fetch_artist(artist)
        if spotify_artist is None:
            logging.info(f"skipped: no artist found: {artist}")
            continue

        # add id and metadata to dataframe
        df.loc[filter_by_artist_(df, artist),
               "spotify_artist_id"] = spotify_artist["id"]
        df.loc[filter_by_artist_(df, artist),
               "spotify_popularity"] = spotify_artist["popularity"]

        # don't trigger spotify rate-limit
        sleep(1)
        if index % 10 == 0:
            total_artists = len(df)
            null_artists = df["spotify_artist_id"].isnull().sum()
            logging.info(f"status: {100 - null_artists / total_artists * 100:.2f} "
                         f"({total_artists - null_artists} / {total_artists}")
    return df


def fetch_bulk_track_features(track_ids):
    fetched_tracks = []
    for i in range(0, len(track_ids), 50):
        chunk = track_ids[i:i + 50]
        print(f"fetching track metadata: {i}")
        tracks = spotify.tracks(chunk)["tracks"]
        sleep(.50)
        print(f"fetching track audio features: {i}")
        track_audio_features = spotify.audio_features(chunk)
        sleep(.50)
        for track, audio_features in zip(tracks, track_audio_features):
            track_ = {
                "id": track["id"],
                "name": track["name"],
                "album": track["album"]["name"],
                "album_id": track["album"]["id"],
                "artists": json.dumps([a["name"] for a in track["artists"]]),
                "artist_ids": json.dumps([a["id"] for a in track["artists"]]),
                "track_number": track["track_number"],
                "disc_number": track["disc_number"],
                "explicit": track["explicit"],
                "duration_ms": track["duration_ms"],
                "year": int(track["album"]["release_date"][0:4]),
                "release_date": track["album"]["release_date"],
                "popularity": track["popularity"],
                "audio_features": 0,
                "isrc": track.get("external_ids", {}).get("isrc")
            }
            if audio_features is not None:
                track_.update({
                    "audio_features": 1,
                    "danceability": audio_features["danceability"],
                    "energy": audio_features["energy"],
                    "key": audio_features["key"],
                    "loudness": audio_features["loudness"],
                    "mode": audio_features["mode"],
                    "speechiness": audio_features["speechiness"],
                    "acousticness": audio_features["acousticness"],
                    "instrumentalness": audio_features["instrumentalness"],
                    "liveness": audio_features["liveness"],
                    "valence": audio_features["valence"],
                    "tempo": audio_features["tempo"],
                    "time_signature": audio_features["time_signature"],
            })
            fetched_tracks.append(track_)
    return fetched_tracks


def enrich_with_artist_nominations_summary(df, artist_nominations_df):
    skip_album_ids = []

    for index, track in df.iterrows():
        print(track["name"], track["artists"])
        if track["album_id"] in skip_album_ids:
            continue
        else:
            skip_album_ids.append(track["album_id"])
        track_ids = json.loads(track["artist_ids"].replace("'", "\""))
        track_release_year = track["release_date"][0:4]
        total_nominations = 0
        total_wins = 0
        first_nomination = []
        first_win = []
        csum_nominations = 0
        csum_wins = 0
        for artist_id in track_ids:
            an_ = artist_nominations_df[artist_nominations_df["spotify_artist_id"] == artist_id]
            if len(an_) > 0:
                an_ = an_.to_dict('records')[0]
                total_nominations += an_["award_nominee"]
                total_wins += an_["award_winner"]
                first_nomination.append(an_["first_nomination"])
                first_win.append(an_["first_win"])
                try:
                    if track_release_year:
                        for year in range(1995, int(track_release_year)):
                            csum_nominations += an_[f"nominated_{year}"]
                            csum_wins += an_[f"win_{year}"]
                except KeyError as err:
                    csum_nominations = 0
                    csum_wins = 0
        df.loc[df["album_id"] == track["album_id"],
               "artist_total_nominations"] = an_["award_nominee"]
        df.loc[df["album_id"] == track["album_id"],
               "artist_total_wins"] = an_["award_winner"]
        df.loc[df["album_id"] == track["album_id"],
               "artist_first_nomination"] = an_["first_nomination"]
        df.loc[df["album_id"] == track["album_id"],
               "artist_first_win"] = an_["first_win"]
        df.loc[df["album_id"] == track["album_id"],
               "artist_csum_nominations"] = csum_nominations
        df.loc[df["album_id"] == track["album_id"],
               "artist_csum_win"] = csum_wins

    return df


def extract_track_ids(df, id_key="id"):
    return list(
        df
        [(~df[id_key].isnull())]
        [id_key].to_dict().values()
    )


def get_artist_info(artist_name):
    artists = mbz.search_artists(artist_name)
    sleep(1)
    if artists["artist-count"] > 0:
        artist = artists["artist-list"][0]
        artist_gender = artist.get("gender")
        artist_country= artist.get("country")
        artist_tags = artist.get("tag-list")
        artist_begin_area = artist.get("begin-area", {}).get("name")
        artist_begin_year = artist.get("life-span", {}).get("begin")
        try:
            top_genre = sorted(artist_tags, key=lambda tag: tag["count"])[-1]["name"]
        except:
            top_genre = None
        artist_releases = mbz.browse_release_groups(artist=artist["id"], limit=100)
        sleep(1)
        try:
            artist_releases_count = len(artist_releases["release-group-list"])
            release_years = [r.get("first-release-date")[0:4] for r in artist_releases["release-group-list"]]
        except:
            artist_releases_count = 0
            release_years = []
        return {
            "gender": artist_gender,
            "country": artist_country,
            #"genre": top_genre,
            "hometown": artist_begin_area,
            # "begin": artist_begin_year,
            # "num_releases": artist_releases_count,
            # "release_years": release_years,
        }
    return {}


def with_mbz_artist_metadata(df, artist_key="artists"):
    """
    Add Spotify ids and metadata to dataframe with artist data
    As ids and metadata are added to multiple rows at a time.
    Make sure to skip rows that already have id and metadata.
    """
    for index, record in df.iterrows():
        artist = record[artist_key]
        artist_ = json.loads(artist)[0]
        logging.info(f"artist: {artist}")
        filter_by_artist_ = filter_by_artist(artist_key=artist_key)

        # check if artist id is already present
        if "artist_genre" in df \
                and len(df[(filter_by_artist_(df, artist))
                           & (df["artist_genre"].isna())]) == 0:
            logging.info("skipped: metadata exists")
            continue

        # search for artist on mbz
        mbz_artist = get_artist_info(artist_)
        if mbz_artist is None:
            logging.info(f"skipped: no artist found: {artist_}")
            continue

        # add id and metadata to dataframe
        df.loc[filter_by_artist_(df, artist),
               "artist_gender"] = mbz_artist.get("gender")
        df.loc[filter_by_artist_(df, artist),
               "artist_country"] = mbz_artist.get("country")
        df.loc[filter_by_artist_(df, artist),
               "artist_genre"] = mbz_artist.get("genre")
        df.loc[filter_by_artist_(df, artist),
               "artist_hometown"] = mbz_artist.get("hometown")
        df.loc[filter_by_artist_(df, artist),
               "artist_begin"] = mbz_artist.get("begin")
        df.loc[filter_by_artist_(df, artist),
               "artist_total_releases"] = mbz_artist.get("num_releases")
        df.loc[filter_by_artist_(df, artist),
               "artist_release_years"] = json.dumps(mbz_artist.get("release_years"))

        if index % 10 == 0:
            total_artists = len(df)
            null_artists = df["artist_genre"].isnull().sum()
            logging.info(f"status: {100 - null_artists / total_artists * 100:.2f} "
                         f"({total_artists - null_artists} / {total_artists}")
    return df
#%%
