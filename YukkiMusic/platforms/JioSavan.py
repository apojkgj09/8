import re

class Saavn:
    def __init__(self):
        self.regex = r'https?://(www\.)?jiosaavn\.com/(song|featured|shows)/.*'

    def is_valid(self, url: str) -> bool:
        return re.match(self.regex, url) is not None
