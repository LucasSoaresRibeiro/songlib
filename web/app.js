let allSongs = [];
let chordsVisible = true; // Global variable to track chord visibility
let songRelationships = {}; // Store song relationships

async function loadAllSongs() {
    try {
        // Load song file list from song_files.txt
        const response = await fetch('web/song_files.txt');
        const fileContent = await response.text();
        const songFiles = fileContent.trim().split('\n');
        
        // Load song relationships
        const relationshipsResponse = await fetch('web/song_relationships.txt');
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
        const songContent = document.getElementById('songContent');
        songContent.innerHTML = '';
        searchInput.value = '';
        searchResults.style.display = 'none';
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

async function loadSongData() {
    try {
        await loadAllSongs();
    } catch (error) {
        console.error('Error loading song data:', error);
    }
}

async function createSongContent(songData) {
    const songContent = document.getElementById('songContent');
    // Clear existing content before displaying new song
    songContent.innerHTML = '';
    songContent.style.display = 'block';
    songContent.style.visibility = 'visible';
    songContent.style.position = 'relative';
    songContent.style.overflow = 'visible';
    
    // Hide the landing page (table) when showing a song
    document.getElementById('landingPage').style.display = 'none';
    
    // Create song header
    const header = document.createElement('div');
    header.innerHTML = `
        <button id="backToTable" class="back-button"><i class="fas fa-arrow-left"></i> Voltar</button>
        <h1>${songData.title}</h1>
        <p class="author">${songData.author}</p>
        <p class="time-sig">${songData.time_sig ? `Compasso: ${songData.time_sig}` : ''}</p>
        <p class="key">Tom: <span>${songData.key}</span></p>
        <button id="toggleChords" class="toggle-chords"><i class="fas fa-guitar"></i>${chordsVisible ? 'Ocultar' : 'Mostrar'} Acordes</button>
        <button class="toggle-share whatsapp-share" onclick="window.open('https://wa.me/?text=${encodeURIComponent(`${songData.title}${songData.author ? ' \n(' + songData.author : ''})

${window.location.href}`)}', '_blank')"><i class="fas fa-share-alt"></i> Compartilhar</button>
        ${songData.url ? `<button class="toggle-youtube" onclick="showYoutubeModal('${songData.url}')"><i class="fab fa-youtube"></i> YouTube</button>` : ''}
        <button class="toggle-print" onclick="window.print()"><i class="fas fa-print"></i> Imprimir</button>
    `;
    songContent.appendChild(header);

    // Add back button functionality
    const backButton = header.querySelector('#backToTable');
    backButton.addEventListener('click', () => {
        // Show the landing page (table)
        document.getElementById('landingPage').style.display = 'flex';
        // Hide song content
        songContent.style.display = 'none';
        // Update URL to remove song parameter
        const url = new URL(window.location);
        url.searchParams.delete('songs');
        window.history.pushState({}, '', url);
    });

    // Add related songs section if available
    const songFileName = `${songData.id}.json`;
    if (songRelationships[songFileName] && songRelationships[songFileName].length > 0) {
        const relatedSongsContainer = document.createElement('div');
        relatedSongsContainer.className = 'related-songs';
        relatedSongsContainer.innerHTML = '<h3>Versões Relacionadas:</h3>';
        
        const relatedList = document.createElement('div');
        relatedList.className = 'related-songs-list';
        
        songRelationships[songFileName].forEach(relatedFileName => {
            const relatedSong = allSongs.find(s => `${s.id}.json` === relatedFileName);
            if (relatedSong) {
                const relatedItem = document.createElement('button');
                relatedItem.className = 'related-song-button';
                relatedItem.innerHTML = `${relatedSong.title} (${relatedSong.key})`;
                relatedItem.addEventListener('click', () => {
                    const url = new URL(window.location);
                    url.searchParams.set('songs', relatedSong.id);
                    window.history.pushState({}, '', url);
                    handleUrlChange();
                });
                relatedList.appendChild(relatedItem);
            }
        });
        
        relatedSongsContainer.appendChild(relatedList);
        header.appendChild(relatedSongsContainer);
    }

    // Add toggle chords functionality
    const toggleChordsBtn = header.querySelector('#toggleChords');
    
    // Initialize chord visibility based on global state
    document.querySelectorAll('.chords').forEach(chord => {
        chord.style.display = chordsVisible ? 'block' : 'none';
    });

    toggleChordsBtn.addEventListener('click', () => {
        chordsVisible = !chordsVisible;
        // toggleChordsBtn.textContent = chordsVisible ? 'Ocultar Acordes' : 'Mostrar Acordes';
        toggleChordsBtn.innerHTML = `<i class="fas fa-guitar"></i>${chordsVisible ? 'Ocultar' : 'Mostrar'} Acordes`;
        document.querySelectorAll('.chords').forEach(chord => {
            chord.style.display = chordsVisible ? 'block' : 'none';
        });
        
        // Toggle compact-lyrics class on lyrics elements when chords are hidden
        document.querySelectorAll('.lyrics').forEach(lyric => {
            lyric.classList.toggle('compact-lyrics', !chordsVisible);
        });
        
        // Update URL while preserving song ID
        const url = new URL(window.location);
        url.searchParams.set('chords', chordsVisible);
        window.history.replaceState({}, '', url);
    });

    // Create chord chart content
    const chordChart = document.createElement('div');
    chordChart.className = 'chordchart';
    
    const lines = songData.chord_chart.split('\n');
    lines.forEach(line => {
        const lineElement = document.createElement('pre');
        
        if (line.trim() === '') {
            lineElement.className = 'empty-line';
            lineElement.innerHTML = '&nbsp;';
        } else if (line.match(/^\s*\[.*\]\s*$/)) {
            lineElement.textContent = line.trim().slice(1, -1).toUpperCase();
            if (line.trim().endsWith('...]')) {
                lineElement.className = 'heading-repetition';
            } else {
                lineElement.className = 'heading';
            }
        } else if (line.startsWith('.')) {
            lineElement.className = 'chords';
            lineElement.textContent = line.substring(1);
        } else {
            lineElement.className = 'lyrics';
            lineElement.textContent = line.toUpperCase();
        }
        
        chordChart.appendChild(lineElement);
    });
    
    songContent.appendChild(chordChart);

    // Wait for content to be fully rendered and fonts to load
    await document.fonts.ready;
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Get the actual dimensions of the content
    const contentRect = songContent.getBoundingClientRect();
    
    // Generate PDF with content-aware dimensions
    const opt = {
        margin: [10, 10, 10, 10],
        filename: `${songData.title}.pdf`,
        image: { type: 'jpeg', quality: 1 },
        html2canvas: { 
            scale: 2,
            useCORS: true,
            logging: true,
            width: contentRect.width,
            height: contentRect.height,
            scrollX: 0,
            scrollY: -window.scrollY
        },
        jsPDF: { 
            unit: 'pt', 
            format: [contentRect.width * 2, contentRect.height * 2],
            orientation: 'portrait',
            compress: true
        }
    };
}

// Create and append modal elements
const modal = document.createElement('div');
modal.id = 'youtubeModal';
modal.className = 'modal';
modal.innerHTML = `
    <div class="modal-content">
        <span class="close-button">&times;</span>
        <div id="youtube-container"></div>
    </div>
`;
document.body.appendChild(modal);

// Function to show YouTube modal
function showYoutubeModal(url) {
    const urlObj = new URL(url);
    let videoId;
    
    if (urlObj.hostname.includes('youtube.com')) {
        videoId = urlObj.searchParams.get('v');
    } else if (urlObj.hostname.includes('youtu.be')) {
        videoId = urlObj.pathname.substring(1);
    }
    
    if (!videoId) return;
    
    // Get additional parameters
    const t = urlObj.searchParams.get('t');
    const startTime = t ? `?start=${t.replace(/[^0-9]/g, '')}` : '';

    const container = document.getElementById('youtube-container');
    container.innerHTML = `<iframe width="320" height="180" src="https://www.youtube.com/embed/${videoId}${startTime}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
    
    const modal = document.getElementById('youtubeModal');
    modal.style.display = 'block';

    // Close modal when clicking the close button or outside the modal
    const closeBtn = modal.querySelector('.close-button');
    closeBtn.onclick = () => {
        modal.style.display = 'none';
        container.innerHTML = '';
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
            container.innerHTML = '';
        }
    };
}

let currentSongIndex = 0;
let songsList = [];

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
        // Hide landing page when a song is in the URL
        document.getElementById('landingPage').style.display = 'none';
    } else {
        songsList = [];
        currentSongIndex = 0;
        // Show landing page when no song is in the URL
        document.getElementById('landingPage').style.display = 'flex';
    }

    // Close YouTube modal if open
    const modal = document.getElementById('youtubeModal');
    if (modal) {
        modal.style.display = 'none';
        const container = document.getElementById('youtube-container');
        if (container) container.innerHTML = '';
    }

    // Clear search results and input
    const searchResults = document.getElementById('searchResults');
    const searchInput = document.getElementById('searchInput');
    if (searchResults) searchResults.style.display = 'none';
    if (searchInput) searchInput.value = '';

    // If songs are loaded, update the display
    if (allSongs.length > 0 && songsList.length > 0) {
        const song = allSongs.find(s => s.id === songsList[currentSongIndex]);
        if (song) {
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
    } else {
        // Clear song content if no songs in URL
        const songContent = document.getElementById('songContent');
        if (songContent) songContent.innerHTML = '';
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
            const urlParams = new URLSearchParams(window.location.search);
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
            const urlParams = new URLSearchParams(window.location.search);
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