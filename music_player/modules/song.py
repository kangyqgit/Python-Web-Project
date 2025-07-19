from dataclasses import dataclass


@dataclass
class Song:
    title: str
    artist: str
    album: str
    year: int
    genre: str
    lyrics: str