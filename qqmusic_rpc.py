import time
import dbus
import requests
from pypresence import Presence, ActivityType

# --- CONFIGURATION ---
CLIENT_ID = '1458558997828468798'
# ---------------------

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
    if not title or "Unknown" in title: return "qqmusic_logo"

    # Query cleanup
    query = f"{title} {artist}".strip()

    try:
        search_url = f"https://c.y.qq.com/soso/fcgi-bin/client_search_cp?p=1&n=1&w={query}&format=json"
        res = requests.get(search_url, timeout=3).json()

        if 'data' in res and 'song' in res['data'] and 'list' in res['data']['song']:
            song_list = res['data']['song']['list']
            if song_list:
                album_mid = song_list[0]['albummid']
                return f"https://y.gtimg.cn/music/photo_new/T002R300x300M000{album_mid}.jpg"

        return "qqmusic_logo"
    except:
        return "qqmusic_logo"

def get_best_player(bus):
    all_names = bus.list_names()
    candidates = [n for n in all_names if "org.mpris.MediaPlayer2" in n]

    # BLOCKLIST
    BROWSER_BLOCKLIST = [
        "helium", "firefox", "google chrome", "brave", "microsoft edge",
        "zen", "librewolf", "vivaldi", "opera", "waterfox", "tor browser"
    ]

    for name in candidates:
        try:
            player_obj = bus.get_object(name, '/org/mpris/MediaPlayer2')
            props = dbus.Interface(player_obj, 'org.freedesktop.DBus.Properties')

            # --- 1. IDENTITY CHECK ---
            identity = str(props.Get('org.mpris.MediaPlayer2', 'Identity')).lower()
            desktop_entry = ""
            try:
                desktop_entry = str(props.Get('org.mpris.MediaPlayer2', 'DesktopEntry')).lower()
            except: pass

            if any(b in identity for b in BROWSER_BLOCKLIST) or any(b in desktop_entry for b in BROWSER_BLOCKLIST):
                continue

            # --- 2. BEHAVIORAL CHECK ---
            try:
                can_go_next = bool(props.Get('org.mpris.MediaPlayer2.Player', 'CanGoNext'))
                can_go_prev = bool(props.Get('org.mpris.MediaPlayer2.Player', 'CanGoPrevious'))

                if not can_go_next:
                    continue
            except Exception:

                continue

            # --- 3. PLAYBACK STATUS CHECK ---
            metadata = props.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
            playback_status = str(props.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))

            if playback_status != "Playing":
                continue

            # --- 4. CHROMIUM URL FILTER ---
            title = str(metadata.get('xesam:title', 'Unknown'))
            url = str(metadata.get('xesam:url', '')).lower()

            if "http://" in url or "https://" in url:
                continue

            if not title or title in ["Unknown", "Unknown Title", ""]:
                continue

            artist_list = metadata.get('xesam:artist', ['Unknown Artist'])
            artist = str(artist_list[0]) if isinstance(artist_list, list) and artist_list else str(artist_list)
            album = str(metadata.get('xesam:album', ''))

            return {
                'title': title,
                'artist': artist,
                'album': album
            }
        except Exception:
            continue

    return None

# --- MAIN LOOP ---
RPC = connect_discord()
bus = dbus.SessionBus()
last_track = ""
last_status = "active"

print("🚀 QQMusic RPC Service Started")

while True:
    if not RPC:
        RPC = connect_discord()
        time.sleep(5)
        continue

    current_song = get_best_player(bus)

    if current_song:

        if current_song['title'] != last_track or last_status == "cleared":
            print(f"🎵 Updating: {current_song['title']}")

            art_url = get_qq_art(current_song['title'], current_song['artist'])

            try:
                RPC.update(
                    activity_type=ActivityType.LISTENING,
                    details=current_song['title'],
                    state=current_song['artist'],
                    large_image=art_url,
                    large_text=current_song['album'] if current_song['album'] else "QQMusic",
                    small_image="qqmusic_logo",
                    start=time.time()
                )
                last_track = current_song['title']
                last_status = "active"
            except Exception as e:
                print(f"❌ Error: {e}")
                # If update fails, force a reconnect on next loop
                RPC = None
    else:
        # No song found
        if last_status == "active":
            print("⏸️ Playback stopped/paused. Clearing status.")
            try:
                RPC.clear()
            except:
                pass
            last_status = "cleared"
            last_track = "" # Reset

    time.sleep(5)
