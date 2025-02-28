let allSongs = [];

async function loadAllSongs() {
    try {
        // Load song file list from song_files.txt
        const response = await fetch('web/song_files.txt');
        const fileContent = await response.text();
        const songFiles = fileContent.trim().split('\n');
        
        // Load full song data for each song file
        const songPromises = songFiles.map(async fileName => {
            const response = await fetch(`songs/${fileName}`);
            const songData = await response.json();
            return songData;
        });

        allSongs = await Promise.all(songPromises);
        setupSearch();
        
        // Check for song ID in URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const songId = urlParams.get('song');
        if (songId) {
            const song = allSongs.find(s => s.id === songId);
            if (song) {
                createSongContent(song);
            }
        }
    } catch (error) {
        console.error('Error loading songs:', error);
    }
}

function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase();
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }

        const filteredSongs = allSongs.filter(song => 
            song.title.toLowerCase().includes(query) ||
            song.author.toLowerCase().includes(query) ||
            (song.chord_chart && song.chord_chart.toLowerCase().includes(query))
        );

        displaySearchResults(filteredSongs);
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
        `;
        resultItem.addEventListener('click', (e) => {
            if (!e.target.classList.contains('share-link')) {
                createSongContent(song);
                searchResults.style.display = 'none';
                document.getElementById('searchInput').value = '';
                // Update URL with song information and set chords to true
                const url = new URL(window.location);
                url.searchParams.set('song', song.id);
                url.searchParams.set('chords', 'true');
                window.history.pushState({}, '', url);
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

function handleKeyChange(event, originalKey) {
    const newKey = event.target.value;
    const chordChart = document.querySelector('.chordchart');
    if (!chordChart) return;

    const semitones = calculateSemitones(originalKey, newKey);
    const transposer = new SongTransposer();
    transposer.transposeSong(chordChart, semitones);
}

function calculateSemitones(fromKey, toKey) {
    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const fromIndex = notes.indexOf(fromKey);
    const toIndex = notes.indexOf(toKey);
    if (fromIndex === -1 || toIndex === -1) return 0;

    let semitones = toIndex - fromIndex;
    if (semitones < -6) semitones += 12;
    if (semitones > 6) semitones -= 12;
    return semitones;
}

async function createSongContent(songData) {
    const songContent = document.getElementById('songContent');
    // Clear existing content before displaying new song
    songContent.innerHTML = '';
    songContent.style.display = 'block';
    songContent.style.visibility = 'visible';
    songContent.style.position = 'relative';
    songContent.style.overflow = 'visible';
    
    // Create song header
    const header = document.createElement('div');
    header.innerHTML = `
        <h1>${songData.title}</h1>
        <p class="author">${songData.author}</p>
        <div class="key-controls">
            <p class="key">Tom: 
                <select id="keySelect" class="key-select" onchange="handleKeyChange(event, '${songData.key}')">
                    ${['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#'].map(k => 
                        `<option value="${k}" ${k === songData.key ? 'selected' : ''}>${k}</option>`
                    ).join('')}
                </select>
            </p>
        </div>
        <button id="toggleChords" class="toggle-chords">Ocultar Acordes</button>
        <button class="toggle-share whatsapp-share" onclick="window.open('https://wa.me/?text=${encodeURIComponent(`${songData.title}${songData.author ? ' \n(' + songData.author : ''})\n\n${window.location.href}`)}', '_blank')">Compartilhar</button>
    `;
    songContent.appendChild(header);

    // Add toggle chords functionality
    const toggleChordsBtn = header.querySelector('#toggleChords');
    const urlParams = new URLSearchParams(window.location.search);
    let chordsVisible = urlParams.get('chords') !== 'false';
    
    // Initialize chord visibility based on URL parameter
    if (!chordsVisible) {
        document.querySelectorAll('.chords').forEach(chord => {
            chord.style.display = 'none';
        });
        toggleChordsBtn.textContent = 'Mostrar Acordes';
    }

    toggleChordsBtn.addEventListener('click', () => {
        chordsVisible = !chordsVisible;
        toggleChordsBtn.textContent = chordsVisible ? 'Ocultar Acordes' : 'Mostrar Acordes';
        document.querySelectorAll('.chords').forEach(chord => {
            chord.style.display = chordsVisible ? 'block' : 'none';
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
        } else if (line.match(/^\[.*\]$/)) {
            lineElement.className = 'heading';
            lineElement.textContent = line.slice(1, -1).toUpperCase();
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
    
    /*
    try {
        // Create a temporary container for PDF generation
        const tempContainer = songContent.cloneNode(true);
        tempContainer.style.position = 'absolute';
        tempContainer.style.left = '0';
        tempContainer.style.top = '0';
        document.body.appendChild(tempContainer);

        const blob = await html2pdf().set(opt).from(tempContainer).output('blob');
        document.body.removeChild(tempContainer);

        if (blob.size === 0) {
            console.error('Generated PDF is empty');
            return;
        }

        const pdfUrl = URL.createObjectURL(blob);
        const pdfContainer = document.getElementById('pdfContainer');
        pdfContainer.innerHTML = `<embed src="${pdfUrl}" type="application/pdf" width="100%" height="100%">`;
        songContent.style.display = 'none';
    } catch (error) {
        console.error('Error generating PDF:', error);
        songContent.style.display = 'block';
    }
    */
}

// Load song data when the page loads
document.addEventListener('DOMContentLoaded', loadSongData);