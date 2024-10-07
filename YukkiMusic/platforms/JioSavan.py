import re
import os
import yt_dlp
import asyncio
from config import seconds_to_time

class SaavnAPI:
    def __init__(self):
        self.base = "https://www.jiosaavn.com/"
        self.regex = r'https?://(www\.)?jiosaavn\.com/(song|featured|shows)/.*'

    async def valid(self, url: str) -> bool:
        return await asyncio.get_event_loop().run_in_executor(None, lambda: re.match(self.regex, url) is not None)

    async def playlist(self, url):
        ydl_opts = {
            'extract_flat': True,
            'force_generic_extractor': True,
            'quiet': True,
        }
        song_info = []
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = await loop.run_in_executor(None, ydl.extract_info, url, False)
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
        return song_info

    @staticmethod
    async def download(url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'geo_bypass': True,
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
        }

        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, ydl.extract_info, url, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            await loop.run_in_executor(None, ydl.download, [url])
            return xyz
