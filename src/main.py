import datetime, time
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from croniter import croniter

from config import Config
from radiofrance import RadioFrance
from spotify import Spotify


def get_previous_timestamp(cron_expression, margin: int = 0):
    """Extract last execution of CRON expression

    Args:
        cron_expression (str): cron valide format expression
        margin (int, optional): seconds of margin. Defaults to 0.

    Returns:
        int: timestamp
    """
    current_time = datetime.datetime.now()
    cron = croniter(cron_expression, current_time)
    previous_time = cron.get_prev(datetime.datetime)
    previous_timestamp = int(previous_time.timestamp() - margin)
    # print("search timestamp", previous_timestamp)
    return previous_timestamp


def sync_playlists(env, spotify):
    # Instantiate objects
    radio = RadioFrance(
        email=env.getenv("RADIO_FRANCE_EMAIL"),
        password=env.getenv("RADIO_FRANCE_PASSWORD"),
        user_id=env.getenv("RF_USER_ID", None),
    )


    timerange = get_previous_timestamp(env.getenv("CRON"), 50)

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
            print(f"{len(uris[0])} morceaux à ajouter à la playlist")
            spotify.add_playlist_items(uris[0])


if __name__ == "__main__":
    env = Config()
    spotify = Spotify(
        client_id=env.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=env.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=env.getenv("SPOTIPY_REDIRECT_URI"),
        playlist=env.getenv("SPOTIFY_PLAYLIST", None),
    )

    scheduler = BlockingScheduler(timezone=env.getenv("TZ", "Europe/Paris"))
    scheduler.add_job(
        sync_playlists,
        CronTrigger.from_crontab(env.getenv("CRON", "*/10 * * * *")),
        args=[env, spotify],
    )
    scheduler.print_jobs()
    scheduler.start()
