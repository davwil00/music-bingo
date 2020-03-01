class Track:

    def __init__(self, artist: str, name: str, preview_url: str) -> None:
        self.artist = artist
        self.name = name
        self.preview_url = preview_url

    def __eq__(self, o: object) -> bool:
        return self.artist == o.artist and \
               self.name == o.name and \
               self.preview_url == o.preview_url

    def __hash__(self) -> int:
        return 27 * hash(self.artist) * hash(self.name) * hash(self.preview_url)
