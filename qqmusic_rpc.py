import time
import re
import dbus
import requests
from pypresence import Presence, ActivityType

POLL_INTERVAL = 5

PLAYERS = {
    "netease": {
        "client_id": "1481279636468928655",
        "small_image": "netease_logo",
        "name": "NetEase Cloud Music",
    },
    "qqmusic": {
        "client_id": "1458558997828468798",
        "small_image": "qqmusic_logo",
        "name": "QQ Music",
    },
}

_art_cache = {}
_current_player_key = None
RPC = None


def connect_discord(client_id):
    try:
        rpc = Presence(client_id)
        rpc.connect()
        print(f"✅ Connected to Discord RPC!")
        return rpc
    except Exception as e:
        print(f"❌ Failed to connect to Discord: {e}")
        return None


def get_itunes_art(title, artist):
    cache_key = (title, artist)
    if cache_key in _art_cache:
        return _art_cache[cache_key]

    queries = [f"{title} {artist}", title]
    stripped = re.sub(r'[\u4e00-\u9fff]+', '', title).strip()
    if stripped and stripped != title:
        queries.append(f"{stripped} {artist}")
        queries.append(stripped)

    for query in queries:
        try:
            res = requests.get(
                "https://itunes.apple.com/search",
                params={"term": query, "media": "music", "limit": 1},
                timeout=5
            ).json()
            results = res.get("results", [])
            if results:
                url = results[0].get("artworkUrl100", "").replace("100x100bb", "600x600bb")
                if url:
                    _art_cache[cache_key] = url
                    return url
        except Exception:
            pass

    _art_cache[cache_key] = None
    return None


def get_best_player(bus):
    BROWSER_BLOCKLIST = [
        "helium", "firefox", "google chrome", "brave", "microsoft edge",
        "zen", "librewolf", "vivaldi", "opera", "waterfox", "tor browser"
    ]

    candidates = [n for n in bus.list_names() if "org.mpris.MediaPlayer2" in n]

    for name in candidates:
        try:
            player_obj = bus.get_object(name, '/org/mpris/MediaPlayer2')
            props = dbus.Interface(player_obj, 'org.freedesktop.DBus.Properties')

            identity = str(props.Get('org.mpris.MediaPlayer2', 'Identity')).lower()
            desktop_entry = ""
            try:
                desktop_entry = str(props.Get('org.mpris.MediaPlayer2', 'DesktopEntry')).lower()
            except Exception:
                pass

            if any(b in identity for b in BROWSER_BLOCKLIST) or any(b in desktop_entry for b in BROWSER_BLOCKLIST):
                continue

            try:
                if not bool(props.Get('org.mpris.MediaPlayer2.Player', 'CanGoNext')):
                    continue
            except Exception:
                continue

            playback_status = str(props.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))
            if playback_status != "Playing":
                continue

            metadata = props.Get('org.mpris.MediaPlayer2.Player', 'Metadata')

            if "http" in str(metadata.get('xesam:url', '')).lower():
                continue

            title = str(metadata.get('xesam:title', ''))
            if not title or title in ["Unknown", "Unknown Title"]:
                continue

            artist_list = metadata.get('xesam:artist', ['Unknown Artist'])
            artist = str(artist_list[0]) if isinstance(artist_list, list) and artist_list else str(artist_list)

            # Identify which player this is
            player_key = "qqmusic"
            for key in PLAYERS:
                if key in identity:
                    player_key = key
                    break

            return {
                'title': title,
                'artist': artist,
                'album': str(metadata.get('xesam:album', '')),
                'mpris_art': str(metadata.get('mpris:artUrl', '')),
                'player_key': player_key,
            }

        except Exception:
            continue

    return None


bus = dbus.SessionBus()
last_track = ""
last_active = False
play_start_time = None

print("🚀 QQ Music / NetEase RPC Service Started")

while True:
    current_song = get_best_player(bus)

    if current_song:
        player_key = current_song['player_key']
        player = PLAYERS[player_key]

        # Switch Discord app if the active player changed
        if player_key != _current_player_key:
            if RPC:
                try:
                    RPC.clear()
                    RPC.close()
                except Exception:
                    pass
            print(f"🔀 Switching to {player['name']}")
            RPC = connect_discord(player['client_id'])
            _current_player_key = player_key
            last_track = ""
            last_active = False

        if not RPC:
            RPC = connect_discord(player['client_id'])
            time.sleep(POLL_INTERVAL)
            continue

        if current_song['title'] != last_track or not last_active:
            print(f"🎵 {player['name']}: {current_song['title']} — {current_song['artist']}")
            play_start_time = time.time()

            # Netease exposes art directly via MPRIS, QQ Music needs iTunes
            if current_song['mpris_art'].startswith("http"):
                art_url = current_song['mpris_art']
            else:
                art_url = get_itunes_art(current_song['title'], current_song['artist']) or player['small_image']

            try:
                RPC.update(
                    activity_type=ActivityType.LISTENING,
                    details=current_song['title'],
                    state=current_song['artist'],
                    large_image=art_url,
                    large_text=current_song['album'] or player['name'],
                    small_image=player['small_image'],
                    start=play_start_time,
                )
                last_track = current_song['title']
                last_active = True
            except Exception as e:
                print(f"❌ RPC update failed: {e}")
                RPC = None
    else:
        if last_active:
            print("⏹️  Playback stopped. Clearing status.")
            try:
                RPC.clear()
            except Exception:
                pass
            last_active = False
            last_track = ""
            play_start_time = None

    time.sleep(POLL_INTERVAL)
