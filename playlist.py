from typing import List

from track import Track


class Playlist:

    def __init__(self, name: str, tracks: List[Track]) -> None:
        self.name = name
        self.tracks = tracks
