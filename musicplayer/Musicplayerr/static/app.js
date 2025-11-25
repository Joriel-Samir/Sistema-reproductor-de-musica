// ============ VARIABLES GLOBALES ============
let playlists = [];      
let songs = [];          
let currentIndex = 0;
let currentPlaylistIndex = 0;
let currentSong = new Audio();

// ============ UTILIDADES ============
function secondsToMinutesSeconds(seconds) {
    if (isNaN(seconds) || seconds < 0) return "00:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

// ============ RENDER PLAYLISTS ============
function renderPlaylists() {
    const container = document.querySelector(".left .library .songList ul");
    container.innerHTML = "";

    playlists.forEach((playlist, idx) => {
        const li = document.createElement("li");
        li.textContent = `${playlist.name} (${playlist.songs.length})`;
        li.style.cursor = "pointer";
        
        if (idx === currentPlaylistIndex) {
            li.style.fontWeight = "bold";
            li.style.color = "#667eea";
        }
        
        li.onclick = () => selectPlaylist(idx);
        container.appendChild(li);
    });
}

// ============ SELECCIONAR PLAYLIST ============
async function selectPlaylist(idx) {
    currentPlaylistIndex = idx;
    currentIndex = 0;
    songs = playlists[idx].songs;
    
    if (songs.length > 0) {
        await setCurrentSongAPI(0);
    }
    
    renderPlaylists();
    renderSongs();
    updatePlayer();
}

// ============ RENDER CANCIONES ============
function renderSongs() {
    const container = document.querySelector(".cardContainer");
    container.innerHTML = "";

    songs.forEach((song, idx) => {
        const card = document.createElement("div");
        card.style.padding = "12px";
        card.style.background = idx === currentIndex ? "#667eea" : "#1a1a1a";
        card.style.color = idx === currentIndex ? "white" : "#fff";
        card.style.margin = "8px";
        card.style.borderRadius = "8px";
        card.style.cursor = "pointer";

        card.innerHTML = `
            <div style="font-weight: 500;">${song.name}</div>
            <div style="font-size: 12px; opacity: 0.7;">
                ${song.artist} • ${song.genre} • ${secondsToMinutesSeconds(song.duration)}
            </div>
        `;

        card.onclick = async () => {
            currentIndex = idx;
            await setCurrentSongAPI(idx);
            renderSongs();
            playMusic(song.url);
        };

        container.appendChild(card);
    });
}

// ============ ACTUALIZAR REPRODUCTOR ============
function updatePlayer() {
    if (!songs[currentIndex]) return;
    const song = songs[currentIndex];
    document.querySelector(".songinfo").innerHTML = song.name;
    document.querySelector(".songtime").innerHTML =
        `00:00 / ${secondsToMinutesSeconds(song.duration)}`;
}

// ============ REPRODUCIR CANCION ============
function playMusic(url) {
    if (!url) return;

    currentSong.src = url;
    currentSong.play();

    document.querySelector("#play").src = "../static/img/pause.svg";
}

// ============ ACTUALIZAR BARRA DE PROGRESO ============
function updateProgressBar() {
    const seekbar = document.querySelector(".seekbar");
    const circle = document.querySelector(".circle");
    
    if (!seekbar || !circle) return;

    const currentTime = currentSong.currentTime;
    const duration = currentSong.duration;

    if (!isNaN(duration) && duration > 0) {
        const percentage = (currentTime / duration) * 100;
        circle.style.left = `${percentage}%`;
        
        document.querySelector(".songtime").innerHTML =
            `${secondsToMinutesSeconds(currentTime)} / ${secondsToMinutesSeconds(duration)}`;
    }
}

// ============ CARGAR BACKEND ============
async function loadDataFromBackend() {
    try {
        const response = await fetch("/api/playlists");
        playlists = await response.json();

        renderPlaylists();

        if (playlists.length > 0) {
            await selectPlaylist(currentPlaylistIndex);  
        }
    } catch (err) {
        console.error("Error cargando playlists:", err);
    }
}

// ============ FUNCIONES API - LISTA CIRCULAR ============

async function nextSongAPI() {
    const playlistName = playlists[currentPlaylistIndex]?.name;
    if (!playlistName) return;

    try {
        const response = await fetch(`/api/playlist/${encodeURIComponent(playlistName)}/next`, {
            method: "POST"
        });
        const data = await response.json();
        
        if (response.ok && data.song) {
            currentIndex = songs.findIndex(s => s.name === data.song.name && s.url === data.song.url);
            
            if (currentIndex === -1) {
                currentIndex = 0;
            }
            
            renderSongs();
            updatePlayer();
            playMusic(data.song.url);
        }
    } catch (err) {
        console.error("Error en next song:", err);
    }
}

async function previousSongAPI() {
    const playlistName = playlists[currentPlaylistIndex]?.name;
    if (!playlistName) return;

    try {
        const response = await fetch(`/api/playlist/${encodeURIComponent(playlistName)}/previous`, {
            method: "POST"
        });
        const data = await response.json();
        
        if (response.ok && data.song) {
            currentIndex = songs.findIndex(s => s.name === data.song.name && s.url === data.song.url);
            
            if (currentIndex === -1) {
                currentIndex = 0;
            }
            
            renderSongs();
            updatePlayer();
            playMusic(data.song.url);
        }
    } catch (err) {
        console.error("Error en previous song:", err);
    }
}

async function setCurrentSongAPI(index) {
    const playlistName = playlists[currentPlaylistIndex]?.name;
    if (!playlistName) return;

    try {
        await fetch(`/api/playlist/${encodeURIComponent(playlistName)}/set_current/${index}`, {
            method: "POST"
        });
    } catch (err) {
        console.error("Error en set current song:", err);
    }
}

async function sortPlaylist(sortBy) {
    const playlistName = playlists[currentPlaylistIndex]?.name;
    if (!playlistName) {
        alert("Selecciona una playlist primero");
        return;
    }
    
    try {
        const response = await fetch(`/api/playlist/${encodeURIComponent(playlistName)}/sort/${sortBy}`, {
            method: "POST"
        });
        
        if (response.ok) {
            await loadDataFromBackend();
        }
    } catch (err) {
        console.error("Error ordenando:", err);
    }
}

// ============ MAIN ============
async function main() {
    await loadDataFromBackend();

    const playBtn = document.querySelector("#play");
    const nextBtn = document.querySelector("#next");
    const prevBtn = document.querySelector("#previous");

    playBtn.addEventListener("click", () => {
        if (currentSong.paused) {
            currentSong.play();
            playBtn.src = "../static/img/pause.svg";
        } else {
            currentSong.pause();
            playBtn.src = "../static/img/play.svg";
        }
    });

    nextBtn.addEventListener("click", () => {
        if (songs.length === 0) return;
        nextSongAPI();
    });

    prevBtn.addEventListener("click", () => {
        if (songs.length === 0) return;
        previousSongAPI();
    });

    currentSong.addEventListener("timeupdate", updateProgressBar);

    currentSong.addEventListener("ended", () => {
        nextSongAPI();
    });

    const seekbar = document.querySelector(".seekbar");
    
    if (seekbar) {
        seekbar.addEventListener("click", (e) => {
            if (isNaN(currentSong.duration)) return;
            
            const seekbarWidth = seekbar.offsetWidth;
            const clickX = e.offsetX;
            const percentage = clickX / seekbarWidth;
            
            currentSong.currentTime = percentage * currentSong.duration;
            updateProgressBar();
        });
    }

    const volumeBar = document.querySelector(".volume input[type='range']");
    
    if (volumeBar) {
        volumeBar.addEventListener("input", (e) => {
            currentSong.volume = e.target.value / 100;
        });
        
        currentSong.volume = 0.5;
        volumeBar.value = 50;
    }

    document.getElementById("addPlaylist").onclick = () => {
        const form = document.getElementById("formPlaylist");
        form.style.display = form.style.display === "none" ? "block" : "none";
    };

    document.getElementById("savePlaylist").onclick = async () => {
        const name = document.getElementById("playlistName").value.trim();
        if (!name) return alert("Escribe un nombre");

        const response = await fetch("/api/add_playlist", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name })
        });

        const data = await response.json();

        if (response.ok) {
            await loadDataFromBackend();
            document.getElementById("playlistName").value = "";
            document.getElementById("formPlaylist").style.display = "none";
        } else {
            alert(data.error);
        }
    };

    const uploadBtn = document.getElementById("addMusic");
    const uploadInput = document.getElementById("uploadFiles");

    uploadBtn.onclick = () => uploadInput.click();

    uploadInput.onchange = async () => {
        const selectedPlaylist = playlists[currentPlaylistIndex]?.name;

        if (!selectedPlaylist) {
            alert("Selecciona una playlist primero");
            return;
        }

        for (const file of uploadInput.files) {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("playlist", selectedPlaylist);

            await fetch("/api/add_song", {
                method: "POST",
                body: formData
            });
        }

        uploadInput.value = "";
        await loadDataFromBackend();
    };
}

main();