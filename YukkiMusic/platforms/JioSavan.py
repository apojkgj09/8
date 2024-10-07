import re
import yt_dlp
from config import seconds_to_time

class Saavn:
    def __init__(self):
        self.base = "https://www.jiosaavn.com/"
        self.regex = r'https?://(www\.)?jiosaavn\.com/(song|featured|shows)/.*'

    def valid(self, url: str) -> bool:
        return re.match(self.regex, url) is not None

    def playlist(self, url):
        ydl_opts = {
            'extract_flat': True,
            'force_generic_extractor': True,
            'quiet': True,
        }
        song_info = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                playlist_info = ydl.extract_info(url, download=False)
                for entry in playlist_info['entries']:
                    duration_sec = entry.get('duration', 0)
                    info = {
                        "title": entry['title'],
                        "duration_sec": duration_sec,
                        "duration_min": seconds_to_time(duration_sec),
                        "thumbnail": entry.get('thumbnail', ''),
                        "webpage_url": entry['url'],
                    }
                    song_info.append(info)
            except Exception:
                pass
        return song_info
