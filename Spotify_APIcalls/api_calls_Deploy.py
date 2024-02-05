import requests
import pandas as pd
from dotenv import load_dotenv

import base64
import os

#load_dotenv(".env")

def get_spotify_access_token():

    client_id = "your_client_id"
    client_secret = "your_client_secret"
    auth_url = "https://accounts.spotify.com/api/token"
    credentials_b64 = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    headers = {"Authorization": f"Basic {credentials_b64}"}
    payload = {"grant_type": "client_credentials"}

    response = requests.post(auth_url, headers=headers, data=payload)
    response.raise_for_status()
    access_token = response.json()['access_token']
    return access_token

def get_artist_id(artist_name, access_token):

    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"q": artist_name, "type": "artist", "limit": 1}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return data['artists']['items'][0]['id'] if data['artists']['items'] else None

def get_related_artists(artist_id, access_token):

    related_artists_url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(related_artists_url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data['artists']

def get_top_tracks_for_artists(artist_ids, access_token, market):
    top_tracks = []

    for artist_id in artist_ids:
        top_tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market={market}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(top_tracks_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        
        for track in data['tracks']:
            artist_name = data["tracks"][0]["artists"][0]["name"]
            top_tracks.append({
                "artist_name": artist_name,
                "track_name": track['name'],
                "popularity": track['popularity'],
                "track_url": track['external_urls']['spotify']
            })
    return top_tracks


def main(artist_name, market):
    access_token = get_spotify_access_token()
    artist_id = get_artist_id(artist_name, access_token)
    if artist_id:
        related_artists = get_related_artists(artist_id, access_token)
        artist_ids = [artist['id'] for artist in related_artists]
        top_tracks = get_top_tracks_for_artists(artist_ids, access_token, market)

        top_tracks_df = pd.DataFrame(top_tracks)
        related_artists_df = pd.DataFrame(related_artists)

        return top_tracks_df, related_artists_df

    else:
        return pd.DataFrame(), pd.DataFrame()

