let allSongs = [];
let chordsVisible = true; // Global variable to track chord visibility
let songRelationships = {}; // Store song relationships
let currentSongData = null; // Store current song data
let originalKey = null; // Store original key for reset functionality
let currentSongIndex = 0;
let songsList = [];

/**
 * Updates the application's visibility states based on the current view.
 * Centralizes all page visibility logic in one function.
 * 
 * @param {string} view - The view to display ('landing', 'song', 'sets')
 * @param {Object} options - Additional options for the view
 */
function updateAppVisibility(view, options = {}) {
    const landingPage = document.getElementById('landingPage');
    const songContent = document.getElementById('songContent');
    const setsPage = document.getElementById('setsPage');
    const navMenu = document.querySelector('.nav-menu');
    const songsLink = document.getElementById('songsLink');
    const setsLink = document.getElementById('setsLink');
    
    // Reset search state
    const searchResults = document.getElementById('searchResults');
    const searchInput = document.getElementById('searchInput');
    if (searchResults) searchResults.style.display = 'none';
    if (searchInput) searchInput.value = '';
    
    // Close YouTube modal if open
    const modal = document.getElementById('youtubeModal');
    if (modal) {
        modal.style.display = 'none';
        const container = document.getElementById('youtube-container');
        if (container) container.innerHTML = '';
    }
    
    // Update visibility based on view
    switch(view) {
        case 'landing':
            landingPage.style.display = 'flex';
            songContent.innerHTML = '';
            setsPage.style.display = 'none';
            if (navMenu) navMenu.style.display = 'flex';
            songsLink.classList.add('active');
            setsLink.classList.remove('active');
            break;
            
        case 'song':
            landingPage.style.display = 'none';
            setsPage.style.display = 'none';
            if (navMenu) navMenu.style.display = 'none';
            break;
            
        case 'sets':
            landingPage.style.display = 'none';
            songContent.innerHTML = '';
            setsPage.style.display = 'flex';
            if (navMenu) navMenu.style.display = 'flex';
            setsLink.classList.add('active');
            songsLink.classList.remove('active');
            break;
            
        default:
            console.error('Unknown view:', view);
    }
}

async function loadAllSongs() {
    try {
        // Load song file list from song_files.txt
        const response = await fetch('web/data/song_files.txt');
        const fileContent = await response.text();
        const songFiles = fileContent.trim().split('\n');
        
        // Load song relationships
        const relationshipsResponse = await fetch('web/data/song_relationships.txt');
        const relationshipsContent = await relationshipsResponse.text();
        const relationships = relationshipsContent.trim().split('\n');
        
        // Parse relationships into a map
        relationships.forEach(line => {
            const relatedSongs = line.replace(/(\r\n|\n|\r)/gm, "").split(',');
            relatedSongs.forEach(song => {
                songRelationships[song] = relatedSongs.filter(s => s !== song);
            });
        });

        // Load full song data for each song file
        const songPromises = songFiles.map(async fileName => {
            const response = await fetch(`songs/${fileName}`);
            const songData = await response.json();
            return songData;
        });

        allSongs = await Promise.all(songPromises);
        setupSearch();
    } catch (error) {
        console.error('Error loading songs:', error);
    }
}

function normalizeText(text) {
    return text
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
        .replace(/[^a-z0-9\s]/g, '') // Remove special characters
        .replace(/\s+/g, ' ') // Normalize spaces
        .trim();
}

function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    // Initialize global chord visibility from URL
    const urlParams = new URLSearchParams(window.location.search);
    chordsVisible = urlParams.get('chords') !== 'false';

    // Add logo click handler for home navigation
    const logo = document.querySelector('.logo');
    logo.style.cursor = 'pointer';
    logo.addEventListener('click', () => {
        updateAppVisibility('landing');
        
        // Update URL to remove song parameter
        const url = new URL(window.location);
        url.searchParams.delete('songs');
        window.history.pushState({}, '', url);
        
        // Display all songs in the table when returning to home
        displaySongsTable(allSongs);
    });

    // Display all songs in the table initially
    displaySongsTable(allSongs);

    searchInput.addEventListener('input', () => {
        const query = normalizeText(searchInput.value);
        
        // Filter songs based on search query
        const filteredSongs = allSongs.filter(song => 
            normalizeText(song.title).includes(query) ||
            normalizeText(song.author || '').includes(query) ||
            (song.chord_chart && normalizeText(song.chord_chart).includes(query))
        );
        
        // Update the table with filtered songs
        displaySongsTable(filteredSongs);
        
        // Show dropdown results only if query has at least 2 characters
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }
        
        // displaySearchResults(filteredSongs);
    });
}

function displaySearchResults(songs) {
    const searchResults = document.getElementById('searchResults');
    searchResults.innerHTML = '';
    searchResults.style.display = songs.length ? 'block' : 'none';

    const query = document.getElementById('searchInput').value.toLowerCase();

    songs.forEach(song => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        
        let matchedPhrase = '';
        if (song.chord_chart && query.length >= 2) {
            const lines = song.chord_chart.split('\n');
            for (const line of lines) {
                if (line.toLowerCase().includes(query) && !line.startsWith('.') && !line.match(/^\[.*\]$/)) {
                    matchedPhrase = line.trim();
                    break;
                }
            }
        }

        resultItem.innerHTML = `
            <strong>${song.title}</strong>
            ${song.author ? `<br>por ${song.author}` : ''}
            ${song.key ? `<br>Tom: ${song.key}` : ''}
            ${matchedPhrase ? `<br><span class="matched-phrase">...${matchedPhrase}...</span>` : ''}
            <div class="search-result-actions">
                <button class="add-to-list"><i class="fas fa-plus"></i> Adicionar na Lista</button>
            </div>
        `;

        // Make the entire result item clickable
        resultItem.style.cursor = 'pointer';
        resultItem.addEventListener('click', (e) => {
            // Don't trigger if clicking the Add to List button
            if (!e.target.closest('.add-to-list')) {
                createSongContent(song);
                searchResults.style.display = 'none';
                document.getElementById('searchInput').value = '';
                const url = new URL(window.location);
                url.searchParams.set('songs', song.id);
                url.searchParams.set('chords', 'true');
                window.history.pushState({}, '', url);
                handleUrlChange();
            }
        });

        // Add to List button click handler
        resultItem.querySelector('.add-to-list').addEventListener('click', (e) => {
            e.stopPropagation();
            const url = new URL(window.location);
            const currentSongs = url.searchParams.get('songs');
            const songIds = currentSongs ? currentSongs.split(',') : [];
            
            if (!songIds.includes(song.id)) {
                songIds.push(song.id);
                url.searchParams.set('songs', songIds.join(','));
                url.searchParams.set('chords', 'true');
                window.history.pushState({}, '', url);
                handleUrlChange();
            }
        });

        searchResults.appendChild(resultItem);
    });
}

// Function to display songs in a table
function displaySongsTable(songs) {
    const songsTableBody = document.getElementById('songsTableBody');
    const noResults = document.getElementById('noResults');
    
    // Clear existing table content
    songsTableBody.innerHTML = '';
    
    // Check if there are songs to display
    if (songs.length === 0) {
        noResults.style.display = 'block';
        return;
    }
    
    noResults.style.display = 'none';
    
    // Sort songs alphabetically by title
    const sortedSongs = [...songs].sort((a, b) => {
        return a.title.localeCompare(b.title, 'pt-BR');
    });
    
    // Add each song to the table
    sortedSongs.forEach(song => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${song.title}</td>
            <td>${song.author || '-'}</td>
            <td>${song.key || '-'}</td>
        `;
        
        // Add click event to open the song
        row.addEventListener('click', () => {
            currentSongData = song;
            createSongContent(song);
            // Update URL with song ID
            const url = new URL(window.location);
            url.searchParams.set('songs', song.id);
            url.searchParams.set('chords', 'true');
            window.history.pushState({}, '', url);
            handleUrlChange();
        });
        
        songsTableBody.appendChild(row);
    });
}

// Function to handle URL changes and reload application state
function handleUrlChange() {
    const urlParams = new URLSearchParams(window.location.search);
    const songsParam = urlParams.get('songs');
    chordsVisible = urlParams.get('chords') !== 'false'; // Update global state

    // Parse songs parameter
    if (songsParam) {
        songsList = songsParam.split(',');
        currentSongIndex = 0;
        // Update visibility for song view
        updateAppVisibility('song');
    } else {
        songsList = [];
        currentSongIndex = 0;
        // Update visibility for landing view
        updateAppVisibility('landing');
    }

    // If songs are loaded, update the display
    if (allSongs.length > 0 && songsList.length > 0) {
        const song = allSongs.find(s => s.id === songsList[currentSongIndex]);
        if (song) {
            currentSongData = song;
            createSongContent(song);
            // Update chord visibility after content is created
            document.querySelectorAll('.chords').forEach(chord => {
                chord.style.display = chordsVisible ? 'block' : 'none';
            });
            // Update lyrics compact class
            document.querySelectorAll('.lyrics').forEach(lyric => {
                lyric.classList.toggle('compact-lyrics', !chordsVisible);
            });
            // Add song navigation controls
            addSongNavigation();
        }
    }
}

function addSongNavigation() {
    const songContent = document.getElementById('songContent');
    const header = songContent.querySelector('header') || songContent.querySelector('h1').parentElement;

    // Create navigation container
    const navContainer = document.createElement('div');
    navContainer.className = 'song-navigation';
    navContainer.innerHTML = `
        <button id="prevSong" ${currentSongIndex === 0 ? 'disabled' : ''}>&lt; Anterior</button>
        <span>${currentSongIndex + 1} / ${songsList.length}</span>
        <button id="nextSong" ${currentSongIndex === songsList.length - 1 ? 'disabled' : ''}>Próxima &gt;</button>
    `;

    // Add navigation event listeners
    navContainer.querySelector('#prevSong').addEventListener('click', () => {
        if (currentSongIndex > 0) {
            currentSongIndex--;
            const song = allSongs.find(s => s.id === songsList[currentSongIndex]);
            if (song) {
                // Close YouTube modal if open
                const modal = document.getElementById('youtubeModal');
                if (modal) {
                    modal.style.display = 'none';
                    const container = document.getElementById('youtube-container');
                    if (container) container.innerHTML = '';
                }
                createSongContent(song);
                // Update chord visibility after content is created
                document.querySelectorAll('.chords').forEach(chord => {
                    chord.style.display = chordsVisible ? 'block' : 'none';
                });
                // Update lyrics compact class
                document.querySelectorAll('.lyrics').forEach(lyric => {
                    lyric.classList.toggle('compact-lyrics', !chordsVisible);
                });
                // Update toggle button text
                const toggleChordsBtn = document.getElementById('toggleChords');
                if (toggleChordsBtn) {
                    toggleChordsBtn.innerHTML = `<i class="fas fa-guitar"></i>${chordsVisible ? 'Ocultar' : 'Mostrar'} Acordes`;
                }
                addSongNavigation();
            }
        }
    });

    navContainer.querySelector('#nextSong').addEventListener('click', () => {
        if (currentSongIndex < songsList.length - 1) {
            currentSongIndex++;
            const song = allSongs.find(s => s.id === songsList[currentSongIndex]);
            if (song) {
                // Close YouTube modal if open
                const modal = document.getElementById('youtubeModal');
                if (modal) {
                    modal.style.display = 'none';
                    const container = document.getElementById('youtube-container');
                    if (container) container.innerHTML = '';
                }
                createSongContent(song);
                // Update chord visibility after content is created
                document.querySelectorAll('.chords').forEach(chord => {
                    chord.style.display = chordsVisible ? 'block' : 'none';
                });
                // Update lyrics compact class
                document.querySelectorAll('.lyrics').forEach(lyric => {
                    lyric.classList.toggle('compact-lyrics', !chordsVisible);
                });
                // Update toggle button text
                const toggleChordsBtn = document.getElementById('toggleChords');
                if (toggleChordsBtn) {
                    toggleChordsBtn.innerHTML = `<i class="fas fa-guitar"></i>${chordsVisible ? 'Ocultar' : 'Mostrar'} Acordes`;
                }
                addSongNavigation();
            }
        }
    });

    // Insert navigation after the header
    if (songsList.length > 1) {
        header.insertAdjacentElement('beforebegin', navContainer);
    }
}

// Add event listeners for URL changes and initial load
window.addEventListener('popstate', handleUrlChange);
document.addEventListener('DOMContentLoaded', () => {
    loadSongData().then(() => handleUrlChange());
});