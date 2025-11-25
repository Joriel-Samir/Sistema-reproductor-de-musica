import os
from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename


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

# ====== RUTA HTML ======
@app.route("/")
def home():
    return render_template("spotify.html")


# ====== RUTA API QUE TU JS ESTÁ BUSCANDO ======
@app.route("/api/playlists")
def get_playlists():
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

    # Buscar playlist
    playlist = next((p for p in playlists if p["name"] == playlist_name), None)
    if not playlist:
        return jsonify({"error": "Playlist no encontrada"}), 404

    # Guardar archivo
    filename = secure_filename(file.filename)
    playlist_folder = os.path.join(UPLOAD_FOLDER, playlist_name)

    os.makedirs(playlist_folder, exist_ok=True)

    path = os.path.join(playlist_folder, filename)
    file.save(path)

    # Registrar canción
    new_song = {
        "name": filename,
        "artist": "Desconocido",
        "genre": "N/A",
        "duration": 180,  
        "url": f"/static/music/{playlist_name}/{filename}"
    }

    playlist["songs"].append(new_song)

    return jsonify({
        "message": "Canción agregada",
        "song": new_song
    })

# ====== INICIO ======
if __name__ == "__main__":
    app.run(debug=True)
