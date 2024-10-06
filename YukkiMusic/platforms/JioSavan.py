import re
import yt_dlp

class Saavn:
    def __init__(self):
        self.base = "https://www.jiosaavn.com/"
        self.regex = r'https?://(www\.)?jiosaavn\.com/(song|featured|shows)/.*'

    def valid(self, url: str) -> bool:
        return re.match(self.regex, url) is not None


    def playlist(playlist_url):
        ydl_opts = {
            'extract_flat': True,
            'force_generic_extractor': True,
            'quiet': True,
        }
        song_info = []
    
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                for entry in playlist_info['entries']:
                    info = {
                        "title": entry['title'],
                        "thumbnail": entry.get('thumbnail', '')
                        "webpage_url": entry['url'],
                    }
                    song_info.append(info)
                return song_info
            except Exception:
                pass
        return song_info
    