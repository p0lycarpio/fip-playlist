import time, os
from urllib.parse import quote
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Spotify:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        playlist: str = None,
    ):
        self.playlist_id = playlist
        self.oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            scope="playlist-modify-private playlist-modify-public",
            redirect_uri=redirect_uri,
        )
        self.sp = None

    def get_token(self, path: str):
        while not os.path.exists(path):
            time.sleep(10)
            print("En attente de l'authentification Spotify...")
        if os.path.isfile(path):
            print("Authentification Spotify réussie !")
            with open(path, "r") as f:
                token = f.read()
            f.close()
        self.oauth.get_access_token(token)
        self.sp = spotipy.Spotify(oauth_manager=self.oauth)

    def add_playlist_items(self, uris: list):
        prepend = "spotify:track:{0}"
        uris = [prepend.format(i) for i in uris]

        if self.playlist_id:
            return self.sp.playlist_add_items(playlist_id=self.playlist_id, items=uris)
        else:
            return self.sp.current_user_saved_tracks_add(tracks=uris)

    def search_track(
        self, query: str, market: str = "FR", limit: int = 1, offset: int = 0
    ) -> str:
        results = self.sp.search(
            q=quote(query), type="track", market=market, limit=limit, offset=offset
        )
        return results["tracks"]["items"][0]["id"]
