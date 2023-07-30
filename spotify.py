from playlist import Playlist


class Spotify:

    def __init__(self) -> None:
        super().__init__()

    def fetch_playlist_tracks(playlist_id) -> Playlist:
        print('Fetching tracks')
        spotify = cc_auth()
        results = spotify.playlist(playlist_id, fields='name,tracks(items(track(preview_url,name,artists(name))))', market='GB')
        tracks = []
        for item in results['tracks']['items']:
            tracks.append(Track(item['track']['artists'][0]['name'],
                                item['track']['name'],
                                item['track']['preview_url']))

        random.shuffle(tracks)
        return Playlist(results['name'], tracks)