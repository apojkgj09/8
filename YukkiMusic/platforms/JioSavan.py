import re
import asyncio
import os
import yt_dlp
from config import seconds_to_time

class SaavnAPI:
    def __init__(self):
        self.loop = asyncio.get_running_loop()
        self.song_regex = r'https?://(www\.)?jiosaavn\.com/song/.*'
        self.playlist_regex = r'https?://(www\.)?jiosaavn\.com/featured/.*'
        self.podcast_regex = r'https?://(www\.)?jiosaavn\.com/shows/.*'
        self.album_regex = r'https?://(www\.)?jiosaavn\.com/album/.*'

    async def valid(self, url: str) -> bool:
        return re.match(self.song_regex, url) is not None

    async def is_song(self, url: str) -> bool:
        return re.match(self.song_regex, url) is not None

    async def is_playlist(self, url: str) -> bool:
        return re.match(self.playlist_regex, url) is not None

    async def is_podcast(self, url: str) -> bool:
        return re.match(self.podcast_regex, url) is not None

    async def is_album(self, url: str) -> bool:
        return re.match(self.album_regex, url) is not None

    async def playlist(self, url):
        def play_list():
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
                            "url": entry['url'],
                        }
                        song_info.append(info)
                except Exception:
                    pass
            return song_info

        return await self.loop.run_in_executor(None, play_list)

    async def download(self, url):
        def down_load():
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'geo_bypass': True,
                'nocheckcertificate': True,
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                file_path = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                
                if os.path.exists(file_path):
                    return file_path, {
                        "title": info['title'],
                        "duration_sec": info.get('duration', 0),
                        "duration_min": seconds_to_time(info.get('duration', 0)),
                        "thumbnail": info.get('thumbnail', ''),
                        "url": info['url'],
                        "filepath":file_path,
                    }

                ydl.download([url])
                return file_path, {
                    "title": info['title'],
                    "duration_sec": info.get('duration', 0),
                    "duration_min": seconds_to_time(info.get('duration', 0)),
                    "thumbnail": info.get('thumbnail', ''),
                    "url": info['url'],
                    "filepath": file_path,
                }

        return await self.loop.run_in_executor(None, down_load)


