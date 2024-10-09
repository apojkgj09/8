import re
import asyncio
import os
import yt_dlp
from config import seconds_to_time


class SaavnAPI:
    def __init__(self):
        self.song_regex = r"https?://(www\.)?jiosaavn\.com/song/.*"
        self.playlist_regex = r"https?://(www\.)?jiosaavn\.com/featured/.*"
        self.podcast_regex = r"https?://(www\.)?jiosaavn\.com/shows/.*"
        self.album_regex = r"https?://(www\.)?jiosaavn\.com/album/.*"

    async def valid(self, url: str) -> bool:
        return "jiosaavn.com" in url

    async def is_song(self, url: str) -> bool:
        return "song" in url

    async def is_playlist(self, url: str) -> bool:
        return "featured" in url

    async def is_podcast(self, url: str) -> bool:
        return "shows" in url

    async def is_album(self, url: str) -> bool:
        return "album" in url

    def clean_url(self, url: str) -> str:
        if "#"in url:
            url = url.split("#")[0]
        return url

    async def playlist(self, url, limit):
        loop = asyncio.get_running_loop()

        clean_url = self.clean_url(url)

        def play_list():
            ydl_opts = {
                "extract_flat": True,
                "force_generic_extractor": True,
                "quiet": True,
            }
            song_info = []
            count = 0
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    playlist_info = ydl.extract_info(clean_url, download=False)
                    for entry in playlist_info["entries"]:
                        if count == limit:
                            break
                        duration_sec = entry.get("duration", 0)
                        info = {
                            "title": entry["title"],
                            "duration_sec": duration_sec,
                            "duration_min": seconds_to_time(duration_sec),
                            "thumb": entry.get("thumbnail", ""),
                            "url": self.clean_url(entry["url"]),
                        }
                        song_info.append(info)
                        count += 1

                except Exception:
                    pass
            return song_info

        return await loop.run_in_executor(None, play_list)

    async def download(self, url):
        loop = asyncio.get_running_loop()

        clean_url = self.clean_url(url)

        def down_load():
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "retries": 3,
                "nooverwrites": False,
                "continuedl": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                file_path = os.path.join("downloads", f"{info['id']}.{info['ext']}")

                if os.path.exists(file_path):
                    return file_path, {
                        "title": info["title"],
                        "duration_sec": info.get("duration", 0),
                        "duration_min": seconds_to_time(info.get("duration", 0)),
                        "thumb": info.get("thumbnail", None),
                        "url": info["url"],
                        "filepath": file_path,
                    }

                ydl.download([clean_url])
                return file_path, {
                    "title": info["title"],
                    "duration_sec": info.get("duration", 0),
                    "duration_min": seconds_to_time(info.get("duration", 0)),
                    "thumb": info.get("thumbnail", None),
                    "url": info["url"],
                    "filepath": file_path,
                }

        return await loop.run_in_executor(None, down_load)
