import os
from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename


# ============ LISTA CIRCULAR - NODO ============
class Node:
    def __init__(self, song):
        self.song = song
        self.next = None


# ============ LISTA ENLAZADA CIRCULAR ============
class CircularLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0
    
    def append(self, song):
        """Agregar canción al final (circular)"""
        new_node = Node(song)
        
        if not self.head:
            self.head = new_node
            self.tail = new_node
            self.current = new_node
            new_node.next = new_node
        else:
            new_node.next = self.head
            self.tail.next = new_node
            self.tail = new_node
        
        self.size += 1
    
    def next(self):
        """Siguiente canción (circular)"""
        if self.current:
            self.current = self.current.next
            return self.current.song
        return None
    
    def previous(self):
        """Canción anterior (circular)"""
        if not self.current or not self.head:
            return None
        
        temp = self.head
        while temp.next != self.current:
            temp = temp.next
        
        self.current = temp
        return self.current.song
    
    def get_current(self):
        """Obtener canción actual"""
        return self.current.song if self.current else None
    
    def set_current(self, index):
        """Establecer canción por índice"""
        if not self.head:
            return None
        
        temp = self.head
        for _ in range(index):
            temp = temp.next
        
        self.current = temp
        return self.current.song
    
    def to_list(self):
        """Convertir a lista de Python"""
        if not self.head:
            return []
        
        result = []
        temp = self.head
        while True:
            result.append(temp.song)
            temp = temp.next
            if temp == self.head:
                break
        
        return result

    def insertion_sort(self, key_func=None):
        """
        Ordenamiento por inserción en lista circular
        key_func: función para obtener la clave de comparación
        Por defecto ordena por nombre de canción
        """
        if not self.head or self.head == self.tail:
            return
        
        if key_func is None:
            key_func = lambda song: song.get('name', '').lower()
        
        self.tail.next = None
        
        sorted_head = None
        current = self.head
        
        while current:
            next_node = current.next
            
            if sorted_head is None or key_func(current.song) < key_func(sorted_head.song):
                current.next = sorted_head
                sorted_head = current
            else:
                search = sorted_head
                while search.next and key_func(search.next.song) < key_func(current.song):
                    search = search.next
                
                current.next = search.next
                search.next = current
            
            current = next_node
        
        self.head = sorted_head
        
        temp = self.head
        while temp.next:
            temp = temp.next
        self.tail = temp
        
        self.tail.next = self.head
        self.current = self.head


# ============ FLASK APP ============

app = Flask(
    __name__,
    template_folder="../Musicplayerr/templates",
    static_folder="../Musicplayerr/static"
)

UPLOAD_FOLDER = "../Musicplayerr/static/music"
ALLOWED_EXT = {"mp3", "wav", "ogg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

playlists = []
circular_lists = {}


# ====== RUTA HTML ======
@app.route("/")
def home():
    return render_template("spotify.html")


# ====== API PLAYLISTS ======
@app.route("/api/playlists")
def get_playlists():
    for playlist in playlists:
        if playlist["name"] not in circular_lists and len(playlist["songs"]) > 0:
            circular_lists[playlist["name"]] = CircularLinkedList()
            for song in playlist["songs"]:
                circular_lists[playlist["name"]].append(song)
    
    return jsonify(playlists)


@app.route("/api/add_playlist", methods=["POST"])
def add_playlist():
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "El nombre está vacío"}), 400

    new_playlist = {
        "name": name,
        "songs": []
    }

    playlists.append(new_playlist)
    circular_lists[name] = CircularLinkedList()

    return jsonify({
        "message": "Playlist creada",
        "playlist": new_playlist
    })


@app.route("/api/add_song", methods=["POST"])
def add_song():
    playlist_name = request.form.get("playlist")
    file = request.files.get("file")

    if not playlist_name:
        return jsonify({"error": "No seleccionaste playlist"}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Archivo no válido"}), 400

    playlist = next((p for p in playlists if p["name"] == playlist_name), None)
    if not playlist:
        return jsonify({"error": "Playlist no encontrada"}), 404

    filename = secure_filename(file.filename)
    playlist_folder = os.path.join(UPLOAD_FOLDER, playlist_name)

    os.makedirs(playlist_folder, exist_ok=True)

    path = os.path.join(playlist_folder, filename)
    file.save(path)

    new_song = {
        "name": filename,
        "artist": "Desconocido",
        "genre": "N/A",
        "duration": 180,  
        "url": f"/static/music/{playlist_name}/{filename}"
    }

    playlist["songs"].append(new_song)
    
    if playlist_name not in circular_lists:
        circular_lists[playlist_name] = CircularLinkedList()
    circular_lists[playlist_name].append(new_song)

    return jsonify({
        "message": "Canción agregada",
        "song": new_song
    })


# ============ NAVEGACIÓN CIRCULAR ============

@app.route("/api/playlist/<playlist_name>/next", methods=["POST"])
def next_song(playlist_name):
    """Obtener siguiente canción (circular)"""
    if playlist_name not in circular_lists:
        return jsonify({"error": "Playlist no encontrada"}), 404
    
    circular_list = circular_lists[playlist_name]
    next_song_data = circular_list.next()
    
    if next_song_data:
        return jsonify({
            "song": next_song_data,
            "message": "Siguiente canción (circular)"
        })
    
    return jsonify({"error": "No hay canciones"}), 404


@app.route("/api/playlist/<playlist_name>/previous", methods=["POST"])
def previous_song(playlist_name):
    """Obtener canción anterior (circular)"""
    if playlist_name not in circular_lists:
        return jsonify({"error": "Playlist no encontrada"}), 404
    
    circular_list = circular_lists[playlist_name]
    prev_song_data = circular_list.previous()
    
    if prev_song_data:
        return jsonify({
            "song": prev_song_data,
            "message": "Canción anterior (circular)"
        })
    
    return jsonify({"error": "No hay canciones"}), 404


@app.route("/api/playlist/<playlist_name>/set_current/<int:index>", methods=["POST"])
def set_current_song(playlist_name, index):
    """Establecer canción actual por índice"""
    if playlist_name not in circular_lists:
        return jsonify({"error": "Playlist no encontrada"}), 404
    
    circular_list = circular_lists[playlist_name]
    current_song_data = circular_list.set_current(index)
    
    if current_song_data:
        return jsonify({
            "song": current_song_data,
            "message": "Canción establecida"
        })
    
    return jsonify({"error": "Índice inválido"}), 400


# ============ ORDENAMIENTO ============

@app.route("/api/playlist/<playlist_name>/sort", methods=["POST"])
def sort_playlist(playlist_name):
    """Ordenar playlist usando insertion sort"""
    data = request.get_json() or {}
    sort_by = data.get("sort_by", "name")
    
    playlist = next((p for p in playlists if p["name"] == playlist_name), None)
    if not playlist:
        return jsonify({"error": "Playlist no encontrada"}), 404
    
    if playlist_name not in circular_lists:
        return jsonify({"error": "Lista circular no inicializada"}), 404
    
    circular_list = circular_lists[playlist_name]
    
    if sort_by == "name":
        key_func = lambda s: s.get('name', '').lower()
    else:
        key_func = lambda s: s.get('name', '').lower()
    
    circular_list.insertion_sort(key_func)
    playlist["songs"] = circular_list.to_list()
    
    return jsonify({
        "message": f"Playlist ordenada por {sort_by}",
        "sorted_by": sort_by,
        "songs": playlist["songs"]
    })


@app.route("/api/playlist/<playlist_name>/sort/name", methods=["POST"])
def sort_by_name(playlist_name):
    """Ordenar por nombre (shortcut)"""
    return sort_playlist_helper(playlist_name, "name")


def sort_playlist_helper(playlist_name, sort_by):
    """Helper para ordenar playlist"""
    playlist = next((p for p in playlists if p["name"] == playlist_name), None)
    if not playlist:
        return jsonify({"error": "Playlist no encontrada"}), 404
    
    if playlist_name not in circular_lists:
        return jsonify({"error": "Lista circular no inicializada"}), 404
    
    circular_list = circular_lists[playlist_name]
    
    if sort_by == "name":
        key_func = lambda s: s.get('name', '').lower()
    else:
        key_func = lambda s: s.get('name', '').lower()
    
    circular_list.insertion_sort(key_func)
    playlist["songs"] = circular_list.to_list()
    
    return jsonify({
        "message": f"Playlist ordenada por {sort_by}",
        "sorted_by": sort_by,
        "songs": playlist["songs"]
    })


# ====== INICIO ======
if __name__ == "__main__":
    app.run(debug=True)