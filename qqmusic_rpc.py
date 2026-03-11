import time
import dbus
import requests
from pypresence import Presence, ActivityType

# --- CONFIGURATION ---
CLIENT_ID = '1458558997828468798'
POLL_INTERVAL = 5  # seconds between checks

# Players to show presence for.
ALLOWED_PLAYERS = [
    "qqmusic",
]
# ---------------------

# Simple in-memory album art cache — avoids re-fetching the same track
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


def get_art(title, artist, mpris_art_url=None):
    """
    Resolve album art URL with layered fallback:
      1. mpris:artUrl  — provided directly by the player (best, no API needed)
      2. QQ Music CDN  — search by title+artist (fallback for players that don't expose art)
      3. qqmusic_logo  — built-in Discord app asset (last resort)
    """
    cache_key = (title, artist)
    if cache_key in _art_cache:
        return _art_cache[cache_key]

    fallback = "qqmusic_logo"

    # Layer 1: use whatever the player already told us
    if mpris_art_url and mpris_art_url.startswith("http"):
        _art_cache[cache_key] = mpris_art_url
        print(f"🖼️  Art from MPRIS: {mpris_art_url[:60]}...")
        return mpris_art_url

    # Layer 2: ask the QQ Music search API
    if title and "Unknown" not in title:
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
                print(f"🖼️  Art from QQ API: {url[:60]}...")
                return url
        except Exception:
            pass

    # Layer 3: logo fallback
    print("🖼️  Art: using logo fallback")
    _art_cache[cache_key] = fallback
    return fallback


def get_best_player(bus):
    """
    Scan MPRIS players on the session bus and return the best candidate.

    Only players whose Identity matches ALLOWED_PLAYERS are considered.
    Priority: Playing > Paused > None

    Returns a dict with keys: title, artist, album, status, art_url, player
    """
    BROWSER_BLOCKLIST = [
        "helium", "firefox", "google chrome", "brave", "microsoft edge",
        "zen", "librewolf", "vivaldi", "opera", "waterfox", "tor browser"
    ]

    all_names = bus.list_names()
    candidates = [n for n in all_names if "org.mpris.MediaPlayer2" in n]

    paused_candidate = None

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

            # Hard-block browsers
            if (any(b in identity for b in BROWSER_BLOCKLIST)
                    or any(b in desktop_entry for b in BROWSER_BLOCKLIST)):
                continue

            # Only allow players in the allowlist
            if not any(p in identity for p in ALLOWED_PLAYERS):
                print(f"⏭️  Skipping player: {identity} (not in ALLOWED_PLAYERS)")
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
                continue

            # --- 4. METADATA ---
            metadata = props.Get('org.mpris.MediaPlayer2.Player', 'Metadata')

            url = str(metadata.get('xesam:url', '')).lower()
            if "http://" in url or "https://" in url:
                continue  # Chromium audio leak

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

            # Grab art URL directly from MPRIS if the player exposes it
            mpris_art = str(metadata.get('mpris:artUrl', ''))

            result = {
                'title': title,
                'artist': artist,
                'album': album,
                'status': playback_status,
                'art_url': mpris_art,
                'player': identity,
            }

            if playback_status == "Playing":
                return result
            elif playback_status == "Paused" and paused_candidate is None:
                paused_candidate = result

        except Exception:
            continue

    return paused_candidate


# --- MAIN LOOP ---
RPC = connect_discord()
bus = dbus.SessionBus()

last_track = ""
last_status = "cleared"   # "playing" | "paused" | "cleared"
play_start_time = None

print("🚀 QQMusic RPC Service Started")
print(f"👀 Watching for players: {', '.join(ALLOWED_PLAYERS)}")

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
            print(f"{label}: {current_song['title']} — {current_song['artist']} [{current_song['player']}]")

            art_url = get_art(
                current_song['title'],
                current_song['artist'],
                mpris_art_url=current_song['art_url'],
            )

            if track_changed and is_playing:
                play_start_time = time.time()
            elif track_changed and not is_playing:
                play_start_time = None

            try:
                RPC.update(
                    activity_type=ActivityType.LISTENING,
                    details=current_song['title'],
                    state=current_song['artist'],
                    large_image=art_url,
                    large_text=current_song['album'] or "QQMusic",
                    small_image="qqmusic_logo",
                    start=play_start_time if is_playing else None,
                )
                last_track = current_song['title']
                last_status = "playing" if is_playing else "paused"

            except Exception as e:
                print(f"❌ RPC update failed: {e}")
                RPC = None

    else:
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
