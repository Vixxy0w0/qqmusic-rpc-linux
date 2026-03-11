import time
import dbus
import requests
import re
from pypresence import Presence, ActivityType

CLIENT_ID = '1458558997828468798'
POLL_INTERVAL = 5

_art_cache = {}


def connect_discord():
    try:
        rpc = Presence(CLIENT_ID)
        rpc.connect()
        print("✅ Connected to Discord RPC!")
        return rpc
    except Exception as e:
        print(f"❌ Failed to connect to Discord: {e}")
        return None


def get_art(title, artist):
    cache_key = (title, artist)
    if cache_key in _art_cache:
        return _art_cache[cache_key]

    queries = [f"{title} {artist}", title]

    # If title has Chinese characters, also try with them stripped out
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

    _art_cache[cache_key] = "qqmusic_logo"
    return "qqmusic_logo"


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

            return {
                'title': title,
                'artist': artist,
                'album': str(metadata.get('xesam:album', '')),
                'status': playback_status,
            }

        except Exception:
            continue

    return None


RPC = connect_discord()
bus = dbus.SessionBus()
last_track = ""
last_active = False
play_start_time = None

print("🚀 QQMusic RPC Service Started")

while True:
    if not RPC:
        RPC = connect_discord()
        time.sleep(POLL_INTERVAL)
        continue

    current_song = get_best_player(bus)

    if current_song:
        if current_song['title'] != last_track or not last_active:
            print(f"🎵 Playing: {current_song['title']} — {current_song['artist']}")
            play_start_time = time.time()

            try:
                RPC.update(
                    activity_type=ActivityType.LISTENING,
                    details=current_song['title'],
                    state=current_song['artist'],
                    large_image=get_art(current_song['title'], current_song['artist']),
                    large_text=current_song['album'] or "QQMusic",
                    small_image="qqmusic_logo",
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
