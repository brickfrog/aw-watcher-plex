# aw-watcher-plex

An [ActivityWatch](https://activitywatch.net/) watcher for [Plex](https://www.plex.tv/) that tracks your media playback activity. Reports what's currently playing on your Plex server to ActivityWatch, including metadata like titles, genres, and playback state. 

[aw-watcher-spotify](https://github.com/ActivityWatch/aw-watcher-spotify) was used as a reference for this implementation and structure. Similar to that, since it's based on the Plex API it will record off-system events that interact with your Plex server.

If you only plan to use this for local device  media I would suggest using [aw-watcher-media-player](https://github.com/2e3s/aw-watcher-media-player) as it can capture a wide source of media and is probably preferred if you're only tracking one device (i.e. you're only using Plex on your desktop/laptop where the watcher is running).

## Features

Tracks your Plex media consumption including:

* Movie and TV show playback with comprehensive metadata including titles, years, genres, and content ratings
* TV show specific information including show titles and season/episode numbers
* Movie specific details such as studio information and ratings
* Device and platform information for each playback session
* Real-time playback state monitoring (playing/paused)

Example of results (from a TV show):

```json
{"id":54612,"timestamp":"2025-01-11T04:59:51.943Z","duration":5.025,"data":{"contentRating":"TV-14","device":"iPhone","duration":2732459,"episode_number":19,"genres":[],"platform":"iOS","player_state":"paused","season_number":5,"show_title":"The X-Files","summary":"Mulder is held hostage inside an office where a man claims his boss is a monster and has clouded all their minds while he turns them into zombies one by one, which is disbelieved until Mulder opens his mind and allows himself to see it too.","title":"Folie à Deux","type":"episode","year":1998}}
```


## Installation

### Requirements

* Python 3.12+
* uv for package management
* A Plex server

### Install the package and dependencies

```bash
git clone https://github.com/brickfrog/aw-watcher-plex
uv venv ~/.local/share/venvs/aw-watcher-plex # or your preferred location for virtual environments
source ~/.local/share/venvs/aw-watcher-plex/bin/activate
uv pip install .
```

## Configuration

Learn how to acquire your Plex authentication token (X-Plex-Token) by following the instructions in the documentation [here](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

The watcher reads its configuration from:

```text
~/.config/activitywatch/aw-watcher-plex/aw-watcher-plex.toml
```

Configure your token and server settings:

```toml
[aw-watcher-plex]
poll_time = 5.0
base_url = "http://localhost:32400"
token = "YOUR-PLEX-TOKEN-HERE"
log_pauses = true # set to false to not log when paused
```

## Usage

Start / test out the watcher by running:

```bash
uv run python aw_watcher_plex/main.py
```

### Automating

I believe it should be picked up due to the `aw-watcher-plex` name, but you can also run it as a system service, I personally like to create a .venv with uv (as above) and then run it as such:


```service
[Unit]
Description=ActivityWatch Plex Watcher
After=aw-server.service

[Service]
Type=simple
ExecStart=/home/user/.local/bin/aw-watcher-plex # or wherever the executable is
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
```

The watcher will:

* Connect to your configured Plex server
* Monitor all active playback sessions
* Report detailed playback activity to ActivityWatch
* Intelligently prioritize playing sessions over paused ones when multiple sessions exist

## Development

### Install development dependencies

```bash
uv pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

## Limitations

This is a basic implementation focused on single-user Plex servers. Current limitations include:

* Only tracks the most recently active session at any given time
* Prioritizes playing sessions over paused ones / still logs when paused - stops when closed
* No support for music or photo libraries
* Limited error handling capabilities
* No multi-user support

## Contributing

This watcher is in early development and welcomes contributions, particularly in these areas areas that address the limitations above / or those that figure out a more elegant metadata structure.