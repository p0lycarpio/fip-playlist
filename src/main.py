from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler

from config import Config
from radiofrance import RadioFrance
from spotify import Spotify


def get_previous_timestamp(interval : int) -> int:
    current_time = datetime.now()
    previous_date = current_time - timedelta(minutes=interval, seconds=10)
    previous_timestamp = int(previous_date.timestamp())
    print("search timestamp", previous_timestamp)
    return previous_timestamp


def sync_playlists(env, spotify) -> None:
    # Instantiate objects
    radio = RadioFrance(
        email=env.getenv("RADIO_FRANCE_EMAIL"),
        password=env.getenv("RADIO_FRANCE_PASSWORD"),
        user_id=env.getenv("RF_USER_ID", None),
    )

    timerange = get_previous_timestamp(int(env.getenv("INTERVAL"), 10))

    # Fetch Radio France likes
    items = radio.get_playlist_items(
        playlist_id=radio.get_playlist(), t_from=timerange, short=False
    )

    if items != None:
        uris = radio.get_tracks_uri(
            [song["id"] for song in items if song["isActive"] == True]
        )

        for orphan in uris[1]:
            artist = orphan["firstLine"]
            title = orphan["secondLine"]
            uris[0].append(
                spotify.search_track(query=f"track:{title} artist:{artist}", limit=1)
            )

        # Append to playlist
        if len(uris[0]) != 0:
            print(f"{len(uris[0])} morceau(x) à ajouter à la playlist")
            spotify.add_playlist_items(uris[0])

    return None


if __name__ == "__main__":
    env = Config()
    spotify = Spotify(
        client_id=env.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=env.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=env.getenv("SPOTIFY_REDIRECT_URI"),
        playlist=env.getenv("SPOTIFY_PLAYLIST", None),
    )
    spotify.get_token("SPOTIFY_TOKEN")

    scheduler = BlockingScheduler(timezone=env.getenv("TZ", "Europe/Paris"))
    scheduler.add_job(
        func=sync_playlists,
        trigger="interval",
        minutes=int(env.getenv("INTERVAL", 10)),
        args=[env, spotify],
    )
    scheduler.print_jobs()
    scheduler.start()
