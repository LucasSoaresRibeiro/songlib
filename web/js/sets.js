// Cache for loaded set data
const setsCache = {};
// Cache for loaded song data
const songsCache = {};

// Function to toggle between pages
function initSetNavigation() {
    const songsLink = document.getElementById('songsLink');
    const setsLink = document.getElementById('setsLink');
    
    songsLink.addEventListener('click', function(e) {
        e.preventDefault();
        updateAppVisibility('landing');
    });
    
    setsLink.addEventListener('click', function(e) {
        e.preventDefault();
        updateAppVisibility('sets');
        loadAllSets();
    });
}

// Function to load set file names from set_files.txt
async function loadSetFilesList() {
    try {
        const response = await fetch('web/data/set_files.txt');
        if (!response.ok) {
            throw new Error('Failed to load set files list');
        }
        
        const text = await response.text();
        return text.split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0);
    } catch (error) {
        console.error('Error loading set files list:', error);
        return [];
    }
}

// Function to load a specific set file
async function loadSetFile(fileName) {
    // Check if we already have this set in cache
    if (setsCache[fileName]) {
        return setsCache[fileName];
    }
    
    try {
        const response = await fetch(`sets/${fileName}`);
        if (!response.ok) {
            throw new Error(`Failed to load set file: ${fileName}`);
        }
        
        const setData = await response.json();
        setsCache[fileName] = setData;
        return setData;
    } catch (error) {
        console.error(`Error loading set file ${fileName}:`, error);
        return null;
    }
}

// Function to load song data from songs/[songId].json
async function loadSongDataForSet(songId) {
    // Check cache first
    if (songsCache[songId]) {
        return songsCache[songId];
    }
    
    try {
        const response = await fetch(`songs/${songId}.json`);
        if (!response.ok) {
            throw new Error(`Failed to load song data for ID: ${songId}`);
        }
        
        const songData = await response.json();
        songsCache[songId] = songData;
        return songData;
    } catch (error) {
        console.error(`Error loading song data for ID ${songId}:`, error);
        return null;
    }
}

// Function to load all sets
async function loadAllSets() {
    const setsContainer = document.getElementById('setsContainer');
    setsContainer.innerHTML = '<p>Carregando repertórios...</p>';
    
    const setFilesList = await loadSetFilesList();
    if (setFilesList.length === 0) {
        setsContainer.innerHTML = '<p>Repertório não encontrado.</p>';
        return;
    }
    
    // Clear container
    setsContainer.innerHTML = '';
    
    // Load all set files first
    const setsPromises = setFilesList.map(fileName => loadSetFile(fileName));
    const setsResults = await Promise.all(setsPromises);
    
    // Create an array of objects with set data and file name
    const sets = [];
    for (let i = 0; i < setsResults.length; i++) {
        if (setsResults[i]) {
            sets.push({
                data: setsResults[i],
                fileName: setFilesList[i]
            });
        }
    }
    
    // Sort sets by date in descending order
    sets.sort((a, b) => {
        const dateA = a.data.date ? new Date(a.data.date) : new Date(0);
        const dateB = b.data.date ? new Date(b.data.date) : new Date(0);
        return dateB - dateA; // Descending order (newest first)
    });
    
    // Display each set in the sorted order
    for (const set of sets) {
        await displaySetCard(setsContainer, set.data, set.fileName);
    }
}

// Function to open a song in the main view
function openSong(songId) {
    // Update visibility state
    updateAppVisibility('song');
    
    // Update URL to load the song
    const url = new URL(window.location);
    url.searchParams.set('songs', songId);
    url.searchParams.set('chords', 'true');
    window.history.pushState({}, '', url);
    
    // Trigger the URL change handler defined in app.js
    if (typeof handleUrlChange === 'function') {
        handleUrlChange();
    }
}

// Function to load all songs in a set
function loadAllSongsInSet(setData) {
    if (!setData.songs || setData.songs.length === 0) {
        alert('This set has no songs to load.');
        return;
    }
    
    // Extract all song IDs from the set
    const songIds = setData.songs.map(song => song.song_id);
    
    // Update visibility state
    updateAppVisibility('song');
    
    // Update URL to load all songs
    const url = new URL(window.location);
    url.searchParams.set('songs', songIds.join(','));
    url.searchParams.set('chords', 'true');
    window.history.pushState({}, '', url);
    
    // Trigger the URL change handler defined in app.js
    if (typeof handleUrlChange === 'function') {
        handleUrlChange();
    }
}

// Function to display a set
async function displaySetCard(container, setData, fileName) {
    const setCard = document.createElement('div');
    setCard.className = 'set-card';
    
    // Create set header
    const setHeader = document.createElement('div');
    setHeader.className = 'set-header';
    
    const titleElement = document.createElement('div');
    titleElement.className = 'set-title';
    titleElement.textContent = setData.title || 'Untitled Set';
    
    // Add draft badge if needed
    if (setData.is_draft) {
        const draftBadge = document.createElement('span');
        draftBadge.className = 'set-draft-badge';
        draftBadge.textContent = 'Rascunho';
        titleElement.appendChild(draftBadge);
    }
    
    const dateElement = document.createElement('div');
    dateElement.className = 'set-date';
    dateElement.textContent = setData.date || 'No date';
    
    setHeader.appendChild(titleElement);
    setHeader.appendChild(dateElement);
    setCard.appendChild(setHeader);
    
    // Add set info if available
    if (setData.notes || setData.leader) {
        const infoElement = document.createElement('div');
        infoElement.className = 'set-info';
        
        if (setData.leader) {
            infoElement.textContent = `Líder: ${setData.leader}`;
        }
        
        if (setData.notes) {
            if (setData.leader) infoElement.textContent += ' | ';
            infoElement.textContent += `Notas: ${setData.notes}`;
        }
        
        setCard.appendChild(infoElement);
    }
    
    // Add "Load All Songs" button
    if (setData.songs && setData.songs.length > 0) {
        const loadButtonContainer = document.createElement('div');
        loadButtonContainer.className = 'set-actions';
        
        const loadButton = document.createElement('button');
        loadButton.className = 'load-set-button';
        loadButton.innerHTML = '<i class="fas fa-music"></i> Carregar Repertório';
        loadButton.title = 'Carregar todas as músicas deste set';
        
        loadButton.addEventListener('click', () => {
            loadAllSongsInSet(setData);
        });
        
        loadButtonContainer.appendChild(loadButton);
        setCard.appendChild(loadButtonContainer);
    }
    
    // Add songs list
    if (setData.songs && setData.songs.length > 0) {
        const songsContainer = document.createElement('div');
        songsContainer.className = 'set-songs';
        
        // Load all song data first
        const songPromises = setData.songs.map(song => loadSongDataForSet(song.song_id));
        const songDataList = await Promise.all(songPromises);
        
        setData.songs.forEach((song, index) => {
            const songElement = document.createElement('div');
            songElement.className = 'set-song';
            
            const songInfo = document.createElement('div');
            songInfo.className = 'set-song-info';
            
            // Use song title if available, fall back to ID if not
            const songData = songDataList[index];
            const songTitle = songData ? songData.title : `Song ID: ${song.song_id}`;
            
            // Create song link
            const songLink = document.createElement('a');
            songLink.href = '#';
            songLink.className = 'song-link';
            songLink.innerHTML = `${index + 1}. ${songTitle} <span class="song-key">(Tom: ${song.key})</span>`;
            
            // Add click event to open the song
            songLink.addEventListener('click', (e) => {
                e.preventDefault();
                openSong(song.song_id);
            });
            
            songInfo.appendChild(songLink);
            songElement.appendChild(songInfo);
            
            if (song.notes) {
                const songNotes = document.createElement('div');
                songNotes.className = 'set-song-notes';
                songNotes.textContent = song.notes;
                songElement.appendChild(songNotes);
            }
            
            songsContainer.appendChild(songElement);
        });
        
        setCard.appendChild(songsContainer);
    } else {
        const noSongs = document.createElement('p');
        noSongs.textContent = 'No songs in this set.';
        setCard.appendChild(noSongs);
    }
    
    // Add file name as data attribute for reference
    setCard.dataset.fileName = fileName;
    
    container.appendChild(setCard);
}

// Function to listen for the back button in song view
function initBackButtonListener() {
    document.addEventListener('click', function(e) {
        if (e.target && (e.target.id === 'backToTable' || e.target.closest('#backToTable'))) {
            // Update visibility with the landing view
            updateAppVisibility('landing');
        }
    });
}

// Initialize navigation and back button listener when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSetNavigation();
    initBackButtonListener();
});