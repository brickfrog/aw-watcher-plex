import logging
import sys
from datetime import datetime, timezone
from time import sleep

from aw_client.client import ActivityWatchClient
from aw_core.config import load_config_toml
from aw_core.models import Event
from plexapi.server import PlexServer

logger = logging.getLogger("aw-watcher-plex")

DEFAULT_CONFIG = """
[aw-watcher-plex]
poll_time = 5.0
base_url = "http://localhost:32400"
token = ""
log_pauses = true
"""


def get_metadata_from_session(session):
    """Extract relevant metadata from a Plex session."""
    # Extract genre names from Genre objects
    genres = []
    if hasattr(session, "genres"):
        genres = [genre.tag for genre in session.genres] if session.genres else []

    data = {
        "title": session.title,
        "type": session.type,
        "player_state": session.player.state
        if hasattr(session.player, "state")
        else "unknown",
        # Basic metadata
        "duration": session.duration if hasattr(session, "duration") else None,
        "year": session.year if hasattr(session, "year") else None,
        # Player info
        "device": session.player.device if hasattr(session.player, "device") else None,
        "platform": session.player.platform
        if hasattr(session.player, "platform")
        else None,
        # Additional metadata from catalog
        "genres": genres,
        "contentRating": session.contentRating
        if hasattr(session, "contentRating")
        else None,
        "summary": session.summary if hasattr(session, "summary") else None,
    }

    # TV Shows
    if session.type == "episode":
        data.update(
            {
                "show_title": session.grandparentTitle
                if hasattr(session, "grandparentTitle")
                else None,
                "season_number": session.parentIndex
                if hasattr(session, "parentIndex")
                else None,
                "episode_number": session.index if hasattr(session, "index") else None,
            }
        )
    # Movies
    elif session.type == "movie":
        data.update(
            {
                "studio": session.studio if hasattr(session, "studio") else None,
                "rating": session.rating if hasattr(session, "rating") else None,
            }
        )

    # Add some debug logging
    logger.info(
        f"Raw session data - duration: {session.duration if hasattr(session, 'duration') else 'N/A'}, "
        f"year: {session.year if hasattr(session, 'year') else 'N/A'}, "
        f"device: {session.player.device if hasattr(session.player, 'device') else 'N/A'}, "
        f"genres: {genres}"
    )
    logger.info(f"Processed metadata: {data}")

    return data


def get_most_recent_session(sessions):
    """Get the most recently active session, prioritizing playing sessions over paused ones."""
    if not sessions:
        return None

    # First, check for any playing sessions
    playing_sessions = [
        s
        for s in sessions
        if hasattr(s.player, "state") and s.player.state == "playing"
    ]
    if playing_sessions:
        # If there are playing sessions, get the most recent one
        return max(
            playing_sessions,
            key=lambda s: getattr(s, "viewOffset", 0)
            if hasattr(s, "viewOffset")
            else 0,
        )

    # If no playing sessions, fall back to most recent paused session
    return max(
        sessions,
        key=lambda s: getattr(s, "viewOffset", 0) if hasattr(s, "viewOffset") else 0,
    )


def main():
    logging.basicConfig(level=logging.INFO)

    # Load config
    config = load_config_toml("aw-watcher-plex", DEFAULT_CONFIG)
    poll_time = float(config["aw-watcher-plex"].get("poll_time", 5.0))
    base_url = config["aw-watcher-plex"].get("base_url", "http://localhost:32400")
    token = config["aw-watcher-plex"].get("token")
    log_pauses = config["aw-watcher-plex"].get("log_pauses", True)

    if not token:
        logger.error("No token specified in config")
        sys.exit(1)

    # Initialize AW
    aw = ActivityWatchClient("aw-watcher-plex", testing=False)
    bucketname = "{}_{}".format(aw.client_name, aw.client_hostname)
    aw.create_bucket(bucketname, "currently-playing")
    aw.connect()

    # Initialize Plex
    plex = PlexServer(base_url, token)
    logger.info(f"Connected to Plex server: {plex.friendlyName}")

    while True:
        try:
            sessions = plex.sessions()

            if sessions:
                session = get_most_recent_session(sessions)
                if hasattr(session.player, "state"):
                    data = get_metadata_from_session(session)
                    
                    # Skip if it's paused and we're not logging pauses
                    if not log_pauses and data["player_state"] != "playing":
                        print("Session paused - skipping due to log_pauses=false")
                        continue

                    state_str = (
                        "Playing" if data["player_state"] == "playing" else "Paused"
                    )
                    if data["type"] == "episode":
                        print(
                            f"{state_str}: {data['show_title']} - S{data['season_number']}E{data['episode_number']} - {data['title']} on {data.get('device', 'Unknown device')}"
                        )
                    else:
                        print(
                            f"{state_str}: {data['title']} on {data.get('device', 'Unknown device')}"
                        )

                    event = Event(timestamp=datetime.now(timezone.utc), data=data)
                    aw.heartbeat(bucketname, event, pulsetime=poll_time + 1)
            else:
                print("No active sessions")

        except Exception as e:
            logger.error(f"Error: {e}")

        sleep(poll_time)


if __name__ == "__main__":
    main()
