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

async function loadSongData() {
    try {
        // Show loading indicator
        const landingPage = document.getElementById('landingPage');
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'loading-indicator';
        loadingIndicator.innerHTML = `
            <div class="loading-spinner"></div>
            <p>Carregando músicas...</p>
        `;
        landingPage.appendChild(loadingIndicator);
        
        // Load songs data
        await loadAllSongs();
        
        // Remove loading indicator after data is loaded
        loadingIndicator.remove();
    } catch (error) {
        console.error('Error loading song data:', error);
        // Show error message to user
        const landingPage = document.getElementById('landingPage');
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-message';
        errorMessage.innerHTML = `
            <p>Erro ao carregar as músicas. Por favor, tente novamente.</p>
            <button onclick="location.reload()">Recarregar</button>
        `;
        landingPage.appendChild(errorMessage);
    }
}

async function createSongContent(songData, isTranposed = false) {
    const songContent = document.getElementById('songContent');
    // Clear existing content before displaying new song
    songContent.innerHTML = '';
    songContent.style.display = 'block';
    songContent.style.visibility = 'visible';
    songContent.style.position = 'relative';
    songContent.style.overflow = 'visible';
    
    // Hide the landing page (table) when showing a song
    document.getElementById('landingPage').style.display = 'none';
    document.title = `${songData.title} - Músicas Maranata`;

    console.log(songData.url.split('|')[0].trim());
    
    // Create song header
    const header = document.createElement('div');
    header.innerHTML = `
        <button id="backToTable" class="back-button"><i class="fas fa-arrow-left"></i> Voltar</button>
        <h1>${songData.title}</h1>
        <p class="author">VERSÃO: ${songData.author}</p>
        <p class="time-sig">${songData.time_sig ? `Compasso: ${songData.time_sig}` : ''}</p>
        <p class="link">REFERÊNCIA: <span>${songData.url.split('|').map(url => url.trim()).join(', ')}</span></p>
        <p class="author key">Tom: <span id="song-key">${songData.key}</span></p>
        <button id="toggleChords" class="toggle-chords"><i class="fas fa-guitar"></i>${chordsVisible ? 'Ocultar' : 'Mostrar'} Acordes</button>
        <button class="toggle-share whatsapp-share" onclick="window.open('https://wa.me/?text=${encodeURIComponent(`${songData.title}${songData.author ? ' \n(' + songData.author : ''})
${window.location.href}`)}', '_blank')"><i class="fas fa-share-alt"></i> Compartilhar</button>
        ${songData.url ? `<button class="toggle-youtube" onclick="showYoutubeModal('${songData.url.split('|')[0].trim()}')"><i class="fab fa-youtube"></i> YouTube</button>` : ''}
        <button id="transposeUp" class="toggle-chords transpose-btn"><i class="fas fa-arrow-up"></i> Subir Tom</button>
        <button id="transposeDown" class="toggle-chords transpose-btn"><i class="fas fa-arrow-down"></i> Descer Tom</button>
        <button id="resetKey" class="toggle-chords transpose-btn"><i class="fas fa-undo"></i> Tom Original</button>
        <button class="toggle-print" onclick="window.print()"><i class="fas fa-print"></i> Imprimir</button>
    `;
    songContent.appendChild(header);

    // Add transpose button functionality
    const transposeUpBtn = header.querySelector('#transposeUp');
    const transposeDownBtn = header.querySelector('#transposeDown');
    
    // Store original key when song is loaded
    originalKey = songData.key;

    if (!isTranposed) {
        currentSongData['key'] = currentSongData['key_original'];
        currentSongData['chord_chart'] = currentSongData['chord_chart_original'];
        currentSongData['key_accumulation'] = 0;
    }

    transposeUpBtn.addEventListener('click', () => transpose('up'));
    transposeDownBtn.addEventListener('click', () => transpose('down'));
    
    // Add reset key functionality
    const resetKeyBtn = header.querySelector('#resetKey');
    resetKeyBtn.addEventListener('click', () => {
        if (currentSongData['chord_chart_original']) {
            currentSongData['key'] = currentSongData['key_original'];
            currentSongData['chord_chart'] = currentSongData['chord_chart_original'];
            currentSongData['key_accumulation'] = 0;
        }
        createSongContent(currentSongData);
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
    addSongNavigation();

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