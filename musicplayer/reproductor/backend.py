from __future__ import annotations


def parse_duration(duration):
    """Convierte una cadena 'MM:SS' a segundos (int).
    Si se pasa un entero en string lo devuelve como int.
    """
    if isinstance(duration, int):
        return duration
    if isinstance(duration, str) and duration.isdigit():
        return int(duration)
    parts = duration.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + int(seconds)
    return 0


class Song:
    """Representa una canción con nombre, artista, duración y género."""
    
    def __init__(self, name, artist, duration, genre):
        self.name = name
        self.artist = artist
        self.duration = duration  # segundos (int)
        self.genre = genre

    @classmethod
    def from_values(cls, name, artist, duration, genre):
        return cls(name=name, artist=artist, duration=parse_duration(duration), genre=genre)

    def __repr__(self):
        mm = self.duration // 60
        ss = self.duration % 60
        return f"{self.name} — {self.artist} [{mm:02d}:{ss:02d}] ({self.genre})"


class SongNode:
    def __init__(self, song, nxt=None):
        self.song = song
        self.next = nxt

    def __repr__(self):
        return f"SongNode({self.song!r})"


class Playlist:
    """Lista simplemente enlazada circular que representa una playlist.
    - Mantiene un puntero `tail` (último nodo) para operaciones eficientes de append.
    - Si está vacía, `tail` es `None`.
    """

    def __init__(self, name):
        self.name = name
        self.tail = None

    def is_empty(self):
        return self.tail is None

    def append(self, song):
        node = SongNode(song)
        if self.tail is None:
            node.next = node
            self.tail = node
        else:
            node.next = self.tail.next
            self.tail.next = node
            self.tail = node

    def __iter_nodes(self):
        if self.tail is None:
            return
        cur = self.tail.next
        while True:
            yield cur
            if cur is self.tail:
                break
            cur = cur.next

    def to_list(self):
        return [node.song for node in self.__iter_nodes()]

    def from_list(self, songs):
        self.tail = None
        for s in songs:
            self.append(s)

    def __repr__(self):
        return f"Playlist({self.name!r}, songs={self.to_list()})"

    def insertion_sort(self, key=None):
        """Ordena la lista usando algoritmo de insertion sort (estable) según `key`.
        Implementación segura para lista circular: transformamos a lista lineal, aplicamos
        insertion sobre nodos y restauramos circularidad.
        """
        if key is None:
            key = lambda s: s.name
            
        if self.tail is None or self.tail.next is self.tail:
            return

        # Romper circularidad: head = tail.next; make tail.next = None
        head = self.tail.next
        self.tail.next = None

        # Insertion sort on singly linked list (stable)
        sorted_head = None

        cur = head
        while cur is not None:
            next_node = cur.next
            # Insert cur into sorted_head
            if sorted_head is None or key(cur.song) < key(sorted_head.song):
                cur.next = sorted_head
                sorted_head = cur
            else:
                spot = sorted_head
                while spot.next is not None and key(spot.next.song) <= key(cur.song):
                    spot = spot.next
                cur.next = spot.next
                spot.next = cur
            cur = next_node

        # Reconstruir circularidad y encontrar tail
        # Find new tail
        new_tail = sorted_head
        if new_tail is None:
            self.tail = None
            return
        while new_tail.next is not None:
            new_tail = new_tail.next
        new_tail.next = sorted_head
        self.tail = new_tail


class PlaylistCollection:
    """Arreglo (lista) de playlists."""

    def __init__(self):
        self.playlists = []

    def add_playlist(self, playlist):
        self.playlists.append(playlist)

    def get_playlist(self, name):
        for p in self.playlists:
            if p.name == name:
                return p
        return None

    def __repr__(self):
        return f"PlaylistCollection({self.playlists!r})"


def _demo():
    # Demo básico: crear playlists, añadir canciones y ordenar
    p = Playlist("Chill Beats")
    p.append(Song.from_values("Calm Night", "Artist A", "03:15", "LoFi"))
    p.append(Song.from_values("Zzz", "Artist B", "02:05", "Ambient"))
    p.append(Song.from_values("Alpha", "Artist C", "04:12", "LoFi"))

    print("Antes:")
    for s in p.to_list():
        print("  ", s)

    # Ordenar por nombre
    p.insertion_sort(key=lambda s: s.name.lower())
    print("\nOrdenado por nombre:")
    for s in p.to_list():
        print("  ", s)

    # Ordenar por duración
    p.insertion_sort(key=lambda s: s.duration)
    print("\nOrdenado por duración:")
    for s in p.to_list():
        print("  ", s)


if __name__ == "__main__":
    _demo()
