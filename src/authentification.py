import os
from flask import Flask, request, redirect
from spotipy import SpotifyOAuth

app = Flask(__name__)
sp = None
auth_manager = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    scope="playlist-modify-private playlist-modify-public",
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
)


@app.route("/")
def index():
    if "code" in request.args:
        token_info = auth_manager.get_access_token(
            code=request.args["code"], as_dict=False, check_cache=True
        )
        with open("SPOTIFY_TOKEN", "w") as f:
            f.write(token_info)
        return "Authentification réussie. Vous pouvez fermer le navigateur"
    else:
        # Rediriger l'utilisateur vers la page de connexion Spotify
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
