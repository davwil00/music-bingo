import configparser
import datetime
import os
import random
import string
import sys
import webbrowser
from collections import defaultdict
from io import BytesIO
from os import path
from typing import List, Set, Tuple, Callable

import pdfkit
import requests
import spotipy
from pydub import AudioSegment
from spotipy import Spotify, oauth2
from spotipy.oauth2 import SpotifyClientCredentials

from number_decoder import strip_additional_info, convert_to_number
from playlist import Playlist
from track import Track

TRACKS_PER_SHEET = 15
NUMBER_OF_SHEETS = 30

BingoSheet = Set[Tuple[Track]]


def cc_auth() -> Spotify:
    client_credentials_manager = SpotifyClientCredentials()
    # return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return spotipy.Spotify('')


def prompt_for_auth():
    print('prompt')
    config = configparser.ConfigParser()
    config.read('props.ini')
    sp_oauth = oauth2.SpotifyOAuth(config['Authorization']['SPOTIPY_CLIENT_ID'],
                                   config['Authorization']['SPOTIPY_CLIENT_SECRET'], "http://localhost:8000")
    auth_url = sp_oauth.get_authorize_url()
    webbrowser.open(auth_url)


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


def generate_bingo_sheets(tracks: List[Track]) -> BingoSheet:
    print('Generating bingo sheets')
    bingo_sheets = set()
    for i in range(0, NUMBER_OF_SHEETS):
        bingo_sheets.add(tuple(random.sample(tracks, TRACKS_PER_SHEET)))

    return bingo_sheets


def simulate_play(bingo_sheets: BingoSheet, tracks: List[Track]) -> List[List[int]]:
    winners = []
    num_of_tracks_matches = defaultdict(int)
    for track_num, track in enumerate(tracks):
        winners_in_rounds = []
        for sheet_num, sheet in enumerate(bingo_sheets):
            if track in sheet:
                num_of_tracks_matches[sheet_num] += 1
                if num_of_tracks_matches[sheet_num] == TRACKS_PER_SHEET:
                    winners_in_rounds.append(sheet_num)
        winners.append(winners_in_rounds)

    return winners


def download_tracks(playlist: Playlist):
    if not path.isdir(f'tracks/{playlist.name}'):
        os.mkdir(f'tracks/{playlist.name}')
    for track in playlist.tracks:
        filename = f'{track.artist} - {track.name}.mp3'
        if track.preview_url is not None:
            if not path.exists(f'tracks/{playlist.name}/{filename}'):
                download_preview(track.preview_url, filename, playlist.name)
        else:
            print(f'missing preview_url, skipping track {track.name}', file=sys.stderr)


def download_preview(url: string, filename: string, folder: str):
    response = requests.get(url)
    raw = BytesIO(response.content)
    with open(f'tracks/{folder}/{filename}', 'wb') as file:
        file.write(raw.read())


def create_bingo_sheet_pdf(bingo_sheets: BingoSheet, name: str, formatters: Tuple[Callable[[str], str], Callable[[str], str]]):
    artist_formatter, track_formatter = formatters
    print(f'Creating bingo sheet for {name}')
    date = datetime.datetime.now()
    html = '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>'
    for sheet_no, sheet in enumerate(bingo_sheets):
        html += '''
<div class="container">
  <h1><span class="emoji">&#x1f3b6;&#x1f3b6;</span>&nbsp; DJ Williams' Music Bingo &nbsp;&#x1f3b6;&#x1f3b6;</h1>
<table>
    <tbody>
'''
        for track_no, track in enumerate(sheet):
            if track_no % 5 == 0:
                if track_no != 0:
                    html += '</tr>\n'
                html += '<tr>\n'
            formatted_track_name = track_formatter(track.name)
            formatted_artist = artist_formatter(track.artist)
            html += f'<td>{formatted_track_name}<br/><span class="artist">{formatted_artist}</span></td>\n'
        html += f'''</tr>
        </tbody>
    </table>
    <p>{date.strftime("%y-%m-%d")} T{sheet_no}</p></div>
'''
    html += '</body></html>'

    options = {
        'page-size': 'A4',
        'margin-top': '1.27cm',
        'margin-right': '1.27cm',
        'margin-bottom': '1.27cm',
        'margin-left': '1.27cm',
        'encoding': "UTF-8",
        'no-outline': None
    }

    with open(f'output/bingo-{name}.html', 'w') as file:
        file.write(html)

    pdfkit.from_string(html, f'output/bingo-{name}.pdf', options=options, css='bingo.css')


def create_single_track(playlist):
    print('Merging tracks')
    whoosh = AudioSegment.from_wav('whoosh.wav')
    single_track = AudioSegment.empty()
    for track in playlist.tracks:
        filename = f'tracks/{playlist.name}/{track.artist} - {track.name}.mp3'
        if path.exists(filename):
            single_track.append(AudioSegment.from_mp3(filename), 0)
            single_track.append(whoosh, 0)
        else:
            print(f'Unable to find track {filename}', file=sys.stderr)

    single_track.export(f'output/bingo-{playlist.name}.mp3')


def run(playlist_id: str, formatters: Tuple[Callable[[str], str], Callable[[str], str]]):
    playlist = fetch_playlist_tracks(playlist_id)

    success = False
    attempt_num = 1

    print('Simulating game:')
    while not success:
        print(f'attempt #{attempt_num}')
        bingo_sheets = generate_bingo_sheets(playlist.tracks)
        winners_in_rounds = simulate_play(bingo_sheets, playlist.tracks)
        winners_in_rounds_with_wins = [round for round in winners_in_rounds if len(round) > 0]
        success = True
        for winners in winners_in_rounds_with_wins[0:3]:
            if len(winners) > 1:
                success = False
                break
        attempt_num += 1
    print_winners(playlist.name, winners_in_rounds)
    create_bingo_sheet_pdf(bingo_sheets, playlist.name, formatters)
    download_tracks(playlist)
    create_single_track(playlist)


def print_winners(playlist_name: str, winners_in_rounds: List[List[int]]):
    with open(f'output/winners - {playlist_name}.txt', 'w') as winners_file:
        for i, round in enumerate(winners_in_rounds):
            if len(round) != 0:
                winners_in_round = [str(ticket_no) for ticket_no in round]
                winners_file.write(f'Winners in round {i} are {",".join(winners_in_round)}\n')


# run('0eScwH7KiLfkSBeHCYwKsz', lambda s: strip_additional_info(s))
run('6z7f5NZTRJ7WGkj5Z9HiYl', (lambda x: '', lambda s: convert_to_number(strip_additional_info(s))))
