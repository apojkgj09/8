import re

class Saavn:
    def __init__(self):
        self.base = "https://www.jiosaavn.com/"
        self.regex = r'https?://(www\.)?jiosaavn\.com/(song|featured|shows)/.*'

    def valid(self, url: str) -> bool:
        return re.match(self.regex, url) is not None
