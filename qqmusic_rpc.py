import time
import dbus
import requests
from pypresence import Presence, ActivityType

# --- CONFIGURATION ---
CLIENT_ID = '1458558997828468798'
POLL_INTERVAL = 5  # seconds between checks
# ---------------------

# Simple in-memory album art cache
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


def get_qq_art(title, artist):
    """Fetch album art URL from QQ Music CDN, with in-memory caching."""
    cache_key = (title, artist)
    if cache_key in _art_cache:
        return _art_cache[cache_key]

    fallback = "qqmusic_logo"

    if not title or "Unknown" in title:
        _art_cache[cache_key] = fallback
        return fallback

    query = f"{title} {artist}".strip()

    try:
        search_url = (
            f"https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
            f"?p=1&n=1&w={query}&format=json"
        )
        res = requests.get(search_url, timeout=3).json()

        song_list = (
            res.get('data', {})
               .get('song', {})
               .get('list', [])
        )
        if song_list:
            album_mid = song_list[0]['albummid']
            url = f"https://y.gtimg.cn/music/photo_new/T002R300x300M000{album_mid}.jpg"
            _art_cache[cache_key] = url
            return url

    except Exception:
        pass  # Network hiccup or bad response — fall through to fallback

    _art_cache[cache_key] = fallback
    return fallback


def get_best_player(bus):
    """
    Scan MPRIS players and return the best candidate.

    Priority: Playing > Paused > None
    Returns a dict with keys: title, artist, album, status
    """
    BROWSER_BLOCKLIST = [
        "helium", "firefox", "google chrome", "brave", "microsoft edge",
        "zen", "librewolf", "vivaldi", "opera", "waterfox", "tor browser"
    ]

    all_names = bus.list_names()
    candidates = [n for n in all_names if "org.mpris.MediaPlayer2" in n]

    paused_candidate = None  # Hold onto a paused player as fallback

    for name in candidates:
        try:
            player_obj = bus.get_object(name, '/org/mpris/MediaPlayer2')
            props = dbus.Interface(player_obj, 'org.freedesktop.DBus.Properties')

            # --- 1. IDENTITY CHECK ---
            identity = str(props.Get('org.mpris.MediaPlayer2', 'Identity')).lower()
            desktop_entry = ""
            try:
                desktop_entry = str(
                    props.Get('org.mpris.MediaPlayer2', 'DesktopEntry')
                ).lower()
            except Exception:
                pass

            if (any(b in identity for b in BROWSER_BLOCKLIST)
                    or any(b in desktop_entry for b in BROWSER_BLOCKLIST)):
                continue

            # --- 2. BEHAVIORAL CHECK ---
            try:
                can_go_next = bool(
                    props.Get('org.mpris.MediaPlayer2.Player', 'CanGoNext')
                )
                if not can_go_next:
                    continue
            except Exception:
                continue

            # --- 3. PLAYBACK STATUS ---
            playback_status = str(
                props.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
            )
            if playback_status == "Stopped":
                continue  # Stopped = no presence at all

            # --- 4. METADATA SANITY CHECKS ---
            metadata = props.Get('org.mpris.MediaPlayer2.Player', 'Metadata')

            url = str(metadata.get('xesam:url', '')).lower()
            if "http://" in url or "https://" in url:
                continue  # Chromium/browser audio leak

            title = str(metadata.get('xesam:title', ''))
            if not title or title in ["Unknown", "Unknown Title"]:
                continue

            artist_list = metadata.get('xesam:artist', ['Unknown Artist'])
            artist = (
                str(artist_list[0])
                if isinstance(artist_list, list) and artist_list
                else str(artist_list)
            )
            album = str(metadata.get('xesam:album', ''))

            result = {
                'title': title,
                'artist': artist,
                'album': album,
                'status': playback_status,  # "Playing" or "Paused"
            }

            if playback_status == "Playing":
                return result  # Best possible match, return immediately
            elif playback_status == "Paused" and paused_candidate is None:
                paused_candidate = result  # Save it

        except Exception:
            continue

    return paused_candidate  # None if nothing found


# --- MAIN LOOP ---
RPC = connect_discord()
bus = dbus.SessionBus()

last_track = ""
last_status = "cleared"   # "playing" | "paused" | "cleared"
play_start_time = None

print("🚀 QQMusic RPC Service Started")

while True:
    if not RPC:
        RPC = connect_discord()
        time.sleep(POLL_INTERVAL)
        continue

    current_song = get_best_player(bus)

    if current_song:
        is_playing = current_song['status'] == "Playing"
        track_changed = current_song['title'] != last_track
        play_state_changed = (
            (is_playing and last_status == "paused")
            or (not is_playing and last_status == "playing")
        )

        if track_changed or play_state_changed or last_status == "cleared":
            label = "🎵 Playing" if is_playing else "⏸️  Paused"
            print(f"{label}: {current_song['title']} — {current_song['artist']}")

            art_url = get_qq_art(current_song['title'], current_song['artist'])

            # Reset the elapsed timer only when a new track starts playing
            if track_changed and is_playing:
                play_start_time = time.time()
            elif track_changed and not is_playing:
                play_start_time = None  # Paused on a new track — no timer yet

            try:
                RPC.update(
                    activity_type=ActivityType.LISTENING,
                    details=current_song['title'],
                    state=current_song['artist'],
                    large_image=art_url,
                    large_text=current_song['album'] or "QQMusic",
                    small_image="qqmusic_logo",
                    # Show elapsed time only when actively playing
                    start=play_start_time if is_playing else None,
                )
                last_track = current_song['title']
                last_status = "playing" if is_playing else "paused"

            except Exception as e:
                print(f"❌ RPC update failed: {e}")
                RPC = None  # Force reconnect on next loop

    else:
        # Nothing playing or paused — clear presence
        if last_status != "cleared":
            print("⏹️  Playback stopped. Clearing status.")
            try:
                RPC.clear()
            except Exception:
                pass
            last_status = "cleared"
            last_track = ""
            play_start_time = None

    time.sleep(POLL_INTERVAL)
