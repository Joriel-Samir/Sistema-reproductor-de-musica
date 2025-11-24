console.log('App.js loaded - Structures from Python backend');

// ============ DATOS DIRECTOS DEL BACKEND PYTHON ============
// En una app real, estos vendrían de: python app.py --json

const MUSIC_DATA = {
  "playlists": [
    {
      "name": "Lo-Fi Chill",
      "songs": [
        {"name": "Calm Night", "artist": "Artist A", "duration": 195, "genre": "Lo-Fi"},
        {"name": "Zzz", "artist": "Artist B", "duration": 125, "genre": "Ambient"},
        {"name": "Alpha", "artist": "Artist C", "duration": 252, "genre": "Lo-Fi"},
        {"name": "Beats", "artist": "Artist D", "duration": 180, "genre": "Lo-Fi"}
      ]
    },
    {
      "name": "Rock Clásico",
      "songs": [
        {"name": "Highway to Hell", "artist": "AC/DC", "duration": 210, "genre": "Rock"},
        {"name": "Bohemian Rhapsody", "artist": "Queen", "duration": 354, "genre": "Rock"},
        {"name": "Smells Like Teen Spirit", "artist": "Nirvana", "duration": 301, "genre": "Grunge"},
        {"name": "Stairway to Heaven", "artist": "Led Zeppelin", "duration": 482, "genre": "Rock"}
      ]
    },
    {
      "name": "Electrónica",
      "songs": [
        {"name": "Around the World", "artist": "Daft Punk", "duration": 240, "genre": "House"},
        {"name": "One More Time", "artist": "Daft Punk", "duration": 300, "genre": "House"},
        {"name": "Clarity", "artist": "Zedd", "duration": 244, "genre": "EDM"}
      ]
    }
  ]
};

// ============ ESTRUCTURAS DE DATOS (Implementadas en Python, replicadas aquí) ============

class Song {
    constructor(name, artist, duration, genre) {
        this.name = name;
        this.artist = artist;
        this.duration = duration; // segundos (int)
        this.genre = genre;
    }

    toString() {
        const mm = Math.floor(this.duration / 60);
        const ss = this.duration % 60;
        return `${this.name} — ${this.artist} [${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}] (${this.genre})`;
    }
}

class SongNode {
    constructor(song, next = null) {
        this.song = song;
        this.next = next;
    }
}

class Playlist {
    constructor(name) {
        this.name = name;
        this.tail = null; // último nodo (circular singly-linked)
    }

    isEmpty() {
        return this.tail === null;
    }

    append(song) {
        const node = new SongNode(song);
        if (this.tail === null) {
            node.next = node;
            this.tail = node;
        } else {
            node.next = this.tail.next;
            this.tail.next = node;
            this.tail = node;
        }
    }

    *iterNodes() {
        if (this.tail === null) return;
        let cur = this.tail.next;
        do {
            yield cur;
            cur = cur.next;
        } while (cur !== this.tail.next);
    }

    toList() {
        return Array.from(this.iterNodes()).map(node => node.song);
    }

    fromList(songs) {
        this.tail = null;
        for (const s of songs) {
            this.append(s);
        }
    }

    insertionSort(keyFn = s => s.name) {
        if (this.tail === null || this.tail.next === this.tail) return;

        // Linearizar
        let head = this.tail.next;
        this.tail.next = null;

        // Insertion sort (estable)
        let sortedHead = null;
        let cur = head;

        while (cur !== null) {
            const nextNode = cur.next;
            
            if (sortedHead === null || keyFn(cur.song) < keyFn(sortedHead.song)) {
                cur.next = sortedHead;
                sortedHead = cur;
            } else {
                let spot = sortedHead;
                while (spot.next !== null && keyFn(spot.next.song) <= keyFn(cur.song)) {
                    spot = spot.next;
                }
                cur.next = spot.next;
                spot.next = cur;
            }
            cur = nextNode;
        }

        // Re-circularizar
        if (sortedHead === null) {
            this.tail = null;
            return;
        }

        let newTail = sortedHead;
        while (newTail.next !== null) {
            newTail = newTail.next;
        }
        newTail.next = sortedHead;
        this.tail = newTail;
    }
}

class PlaylistCollection {
    constructor() {
        this.playlists = [];
    }

    addPlaylist(playlist) {
        this.playlists.push(playlist);
    }

    getPlaylist(name) {
        return this.playlists.find(p => p.name === name);
    }
}

// ============ INICIALIZAR DATOS ============

let collection = new PlaylistCollection();

// Cargar datos desde MUSIC_DATA
for (const playlistData of MUSIC_DATA.playlists) {
    const playlist = new Playlist(playlistData.name);
    for (const songData of playlistData.songs) {
        const song = new Song(songData.name, songData.artist, songData.duration, songData.genre);
        playlist.append(song);
    }
    collection.addPlaylist(playlist);
}

console.log('Colección creada:', collection);

// ============ LÓGICA DEL REPRODUCTOR ============

let currentSong = new Audio();
let songs = [];
let currFolder = '';
let currentPlaylist = null;
let currentIndex = 0;

function secondsToMinutesSeconds(seconds) {
    if (isNaN(seconds) || seconds < 0) {
        return "00:00";
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

function renderPlaylists() {
    const container = document.querySelector(".left .library .songList ul");
    container.innerHTML = "";
    collection.playlists.forEach((playlist, idx) => {
        const li = document.createElement("li");
        li.textContent = `${playlist.name} (${playlist.toList().length})`;
        li.style.cursor = "pointer";
        li.style.padding = "8px";
        li.style.borderBottom = "1px solid #333";
        li.onclick = () => selectPlaylist(idx);
        container.appendChild(li);
    });
}

function selectPlaylist(idx) {
    currentPlaylist = collection.playlists[idx];
    songs = currentPlaylist.toList();
    currentIndex = 0;
    renderSongs();
    updatePlayer();
}

function renderSongs() {
    const container = document.querySelector(".cardContainer");
    container.innerHTML = "";
    
    if (!currentPlaylist) return;
    
    songs.forEach((song, idx) => {
        const div = document.createElement("div");
        div.style.padding = "12px";
        div.style.background = "#1a1a1a";
        div.style.margin = "8px";
        div.style.borderRadius = "8px";
        div.style.cursor = "pointer";
        div.style.transition = "all 0.3s";
        if (idx === currentIndex) {
            div.style.background = "#667eea";
            div.style.color = "white";
            div.style.fontWeight = "bold";
        }
        
        div.innerHTML = `
            <div style="font-weight: 500;">${song.name}</div>
            <div style="font-size: 12px; opacity: 0.7;">${song.artist} • ${song.genre} • ${secondsToMinutesSeconds(song.duration)}</div>
        `;
        
        div.onmouseover = () => div.style.background = "#667eea";
        div.onmouseout = () => {
            if (idx !== currentIndex) div.style.background = "#1a1a1a";
        };
        
        div.onclick = () => {
            currentIndex = idx;
            renderSongs();
            playMusic(songs[idx].name, false);
        };
        
        container.appendChild(div);
    });
}

function updatePlayer() {
    if (!songs || !songs[currentIndex]) return;
    const song = songs[currentIndex];
    document.querySelector(".songinfo").innerHTML = song.name;
    document.querySelector(".songtime").innerHTML = "00:00 / " + secondsToMinutesSeconds(song.duration);
}

function playMusic(trackName = null, pause = false) {
    if (trackName) {
        const idx = songs.findIndex(s => s.name === trackName);
        if (idx >= 0) currentIndex = idx;
    }
    
    updatePlayer();
    
    if (!pause) {
        document.querySelector("#play").src = "../static/img/pause.svg";
        console.log("▶ Reproduciendo:", songs[currentIndex].name);
    }
}

async function main() {
    console.log("Inicializando reproductor...");
    
    // Renderizar playlists en el sidebar
    renderPlaylists();
    
    // Seleccionar primera playlist
    if (collection.playlists.length > 0) {
        selectPlaylist(0);
        playMusic(null, true);
    }

    // Event listeners
    const play = document.querySelector("#play");
    const next = document.querySelector("#next");
    const previous = document.querySelector("#previous");
    
    if (play) {
        play.addEventListener("click", () => {
            if (currentSong.paused) {
                playMusic(null, false);
            } else {
                currentSong.pause();
                play.src = "../static/img/play.svg";
            }
        });
    }

    if (next) {
        next.addEventListener("click", () => {
            if (songs.length > 0) {
                currentIndex = (currentIndex + 1) % songs.length;
                renderSongs();
                playMusic(null, false);
            }
        });
    }

    if (previous) {
        previous.addEventListener("click", () => {
            if (songs.length > 0) {
                currentIndex = (currentIndex - 1 + songs.length) % songs.length;
                renderSongs();
                playMusic(null, false);
            }
        });
    }

    // Listen for timeupdate
    currentSong.addEventListener("timeupdate", () => {
        document.querySelector(".songtime").innerHTML = `${secondsToMinutesSeconds(currentSong.currentTime)} / ${secondsToMinutesSeconds(currentSong.duration)}`;
        const circle = document.querySelector(".circle");
        if (currentSong.duration) {
            circle.style.left = (currentSong.currentTime / currentSong.duration) * 100 + "%";
        }
    });

    // Seekbar
    const seekbar = document.querySelector(".seekbar");
    if (seekbar) {
        seekbar.addEventListener("click", e => {
            let percent = (e.offsetX / seekbar.getBoundingClientRect().width);
            document.querySelector(".circle").style.left = percent * 100 + "%";
            currentSong.currentTime = percent * currentSong.duration;
        });
    }

    // Hamburger
    const hamburger = document.querySelector(".hamburger");
    if (hamburger) {
        hamburger.addEventListener("click", () => {
            document.querySelector(".left").style.left = "0";
        });
    }

    // Close
    const close = document.querySelector(".close");
    if (close) {
        close.addEventListener("click", () => {
            document.querySelector(".left").style.left = "-120%";
        });
    }

    // Volume
    const volumeInput = document.querySelector(".range input");
    if (volumeInput) {
        volumeInput.addEventListener("change", (e) => {
            currentSong.volume = parseInt(e.target.value) / 100;
        });
    }

    // Mute
    const volumeImg = document.querySelector(".volume>img");
    if (volumeImg) {
        volumeImg.addEventListener("click", e => {
            if (e.target.src.includes("volume.svg")) {
                e.target.src = e.target.src.replace("volume.svg", "mute.svg");
                currentSong.volume = 0;
                if (volumeInput) volumeInput.value = 0;
            } else {
                e.target.src = e.target.src.replace("mute.svg", "volume.svg");
                currentSong.volume = 0.1;
                if (volumeInput) volumeInput.value = 10;
            }
        });
    }
}

main();
