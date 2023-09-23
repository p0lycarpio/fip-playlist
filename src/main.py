import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from croniter import croniter

from config import Config
from radiofrance import RadioFrance
from spotify import Spotify


def get_previous_timestamp(cron_expression):
    """Extract the execution timestamp before the current time for the given CRON expression.

    Args:
        cron_expression (str): Valid cron format expression (e.g., "*/10 * * * *").

    Returns:
        int: Timestamp of the previous execution.
    """
    current_time = datetime.datetime.now()
    cron = croniter(cron_expression, current_time)
    
    # Remonter dans le temps jusqu'à obtenir une exécution antérieure
    while True:
        previous_time = cron.get_prev(datetime.datetime)
        if previous_time < current_time:
            break
        cron.get_prev(datetime.datetime)  # Obtenir la précédente, puis vérifier à nouveau

    previous_timestamp = int(previous_time.timestamp())
    print("search timestamp", previous_timestamp)
    return previous_timestamp


def sync_playlists(env, spotify) -> None:
    # Instantiate objects
    radio = RadioFrance(
        email=env.getenv("RADIO_FRANCE_EMAIL"),
        password=env.getenv("RADIO_FRANCE_PASSWORD"),
        user_id=env.getenv("RF_USER_ID", None),
    )

    timerange = get_previous_timestamp(env.getenv("CRON"))

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
        trigger=CronTrigger.from_crontab(env.getenv("CRON", "*/10 * * * *")),
        args=[env, spotify],
    )
    scheduler.print_jobs()
    scheduler.start()
