#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Backend Python puro para el reproductor de música.
Expone las estructuras de datos directamente para que app.js las use.
"""

import sys
import json
from pathlib import Path

# Importar las estructuras de datos
sys.path.insert(0, str(Path(__file__).parent))
from backend import Song, SongNode, Playlist, PlaylistCollection, parse_duration


def create_demo_collection():
    """Crea una colección de demo con playlists y canciones."""
    collection = PlaylistCollection()
    
    # Playlist 1: Lo-Fi Chill
    lofi = Playlist("Lo-Fi Chill")
    lofi.append(Song.from_values("Penedol", "Artist A", "03:15", "Lo-Fi"))
    lofi.append(Song.from_values("Zzz", "Artist B", "02:05", "Ambient"))
    lofi.append(Song.from_values("Alpha", "Artist C", "04:12", "Lo-Fi"))
    lofi.append(Song.from_values("Beats", "Artist D", "03:00", "Lo-Fi"))
    collection.add_playlist(lofi)
    
    # Playlist 2: Rock Clásico
    rock = Playlist("Chat gpt es la vg")
    rock.append(Song.from_values("Highway to Hell", "AC/DC", "03:30", "Rock"))
    rock.append(Song.from_values("Bohemian Rhapsody", "Queen", "05:54", "Rock"))
    rock.append(Song.from_values("Smells Like Teen Spirit", "Nirvana", "05:01", "Grunge"))
    rock.append(Song.from_values("Stairway to Heaven", "Led Zeppelin", "08:02", "Rock"))
    collection.add_playlist(rock)
    
    # Playlist 3: Electrónica
    electronic = Playlist("Electrónica")
    electronic.append(Song.from_values("Around the World", "Daft Punk", "04:00", "House"))
    electronic.append(Song.from_values("One More Time", "Daft Punk", "05:00", "House"))
    electronic.append(Song.from_values("Clarity", "Zedd", "04:04", "EDM"))
    collection.add_playlist(electronic)
    
    return collection


def serialize_collection(collection):
    """Serializa la colección a JSON para enviársela a JavaScript."""
    playlists = []
    for playlist in collection.playlists:
        songs = []
        for song in playlist.to_list():
            songs.append({
                "name": song.name,
                "artist": song.artist,
                "duration": song.duration,
                "genre": song.genre,
            })
        playlists.append({
            "name": playlist.name,
            "songs": songs,
        })
    return {"playlists": playlists}


def main():
    """Punto de entrada: prueba las estructuras."""
    print("🎵 Backend de Reproductor de Música")
    print("=" * 50)
    
    # Crear colección de demo
    collection = create_demo_collection()
    
    # Mostrar playlists
    for i, playlist in enumerate(collection.playlists, 1):
        print(f"\n📚 Playlist {i}: {playlist.name}")
        for j, song in enumerate(playlist.to_list(), 1):
            print(f"  {j}. {song}")
    
    # Probar ordenamiento
    print("\n" + "=" * 50)
    print("🔤 Prueba: Ordenar 'Rock Clásico' por nombre")
    rock = collection.get_playlist("Rock Clásico")
    rock.insertion_sort(key=lambda s: s.name.lower())
    for j, song in enumerate(rock.to_list(), 1):
        print(f"  {j}. {song}")
    
    print("\n⏱ Prueba: Ordenar 'Rock Clásico' por duración")
    rock.insertion_sort(key=lambda s: s.duration)
    for j, song in enumerate(rock.to_list(), 1):
        print(f"  {j}. {song}")
    
    # Serializar para JavaScript
    print("\n" + "=" * 50)
    print("📤 JSON para JavaScript:")
    data = serialize_collection(collection)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
