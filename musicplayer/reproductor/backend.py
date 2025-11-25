from flask import Flask, jsonify, request
from server import Playlist, PlaylistCollection, Song  

app = Flask(__name__)

# ============ CREAR LA COLECCIÓN DE PLAYLISTS ============

