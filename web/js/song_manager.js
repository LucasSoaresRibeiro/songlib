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

/**
 * Filtros CSS no elemento html ou no container do YouTube impedem o carregamento ou a exibição
 * do vídeo em iframes no Safari antigo (iPad). Guardamos e removemos enquanto o modal está aberto.
 */
var _youtubeModalSavedFilters = null;

function suspendFiltersForYoutubeEmbed() {
    if (_youtubeModalSavedFilters !== null) {
        return;
    }
    var container = document.getElementById('youtube-container');
    _youtubeModalSavedFilters = {
        html: document.documentElement.style.filter || '',
        container: container ? container.style.filter || '' : ''
    };
    document.documentElement.style.filter = '';
    if (container) {
        container.style.filter = '';
    }
}

function restoreYoutubeModalFilters() {
    if (_youtubeModalSavedFilters === null) {
        return;
    }
    document.documentElement.style.filter = _youtubeModalSavedFilters.html;
    var container = document.getElementById('youtube-container');
    if (container) {
        container.style.filter = _youtubeModalSavedFilters.container;
    }
    _youtubeModalSavedFilters = null;
}

async function loadSongData() {
    const landingPage = document.getElementById('landingPage');
    let loadingIndicator = null;
    try {
        if (landingPage) {
            loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'loading-indicator';
            loadingIndicator.innerHTML = `
            <div class="loading-spinner"></div>
            <p>Carregando músicas e programações...</p>
        `;
            landingPage.appendChild(loadingIndicator);
        }

        await Promise.all([loadAllSongs(), loadAllSets()]);

        if (loadingIndicator) {
            loadingIndicator.remove();
        }

        await handleUrlChange();
    } catch (error) {
        console.error('Error loading song data:', error);
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
        const msg =
            (error && error.message) ||
            'Erro ao carregar os dados. Verifique o slug da igreja (?church=) e a rede.';
        if (landingPage) {
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error-message';
            errorMessage.innerHTML = `
            <p>${msg}</p>
            <button onclick="location.reload()">Recarregar</button>
        `;
            landingPage.appendChild(errorMessage);
        }
    }
}

function createSongContent(songData) {

    const songContent = document.getElementById('songContent');
    // Clear existing content before displaying new song
    songContent.innerHTML = '';
    songContent.style.display = 'block';
    songContent.style.visibility = 'visible';
    songContent.style.position = 'relative';
    songContent.style.overflow = 'visible';
    
    const landingPageEl = document.getElementById('landingPage');
    if (landingPageEl) landingPageEl.style.display = 'none';
    document.title = `${songData.title} - Músicas Maranata`;

    let keyAccumulationLabel = "";
    if (currentSongData['key_accumulation'] > 0) {
        keyAccumulationLabel = `(+${currentSongData['key_accumulation']})`;
    } else if (currentSongData['key_accumulation'] < 0) {
        keyAccumulationLabel = `(${currentSongData['key_accumulation']})`;
    }
    
    const refLine = (songData.url || '')
        .split('|')
        .map(url => url.trim())
        .filter(Boolean)
        .join(', ');
    const sharePageUrl = typeof getPublicShareUrlForSong === 'function'
        ? getPublicShareUrlForSong(songData.id)
        : `${window.location.origin}${window.location.pathname}?songs=${encodeURIComponent(String(songData.id))}`;
    const waText = `${songData.title}${songData.author ? '\n(' + songData.author + ')' : ''}\n${sharePageUrl}`;
    const firstVideoUrl = (songData.url || '').split('|')[0].trim();

    // Create song header
    const header = document.createElement('div');
    header.innerHTML = `
        <h1>${songData.title}</h1>
        <p class="author">VERSÃO: ${songData.author}</p>
        <p class="time-sig">${songData.time_sig ? `Compasso: ${songData.time_sig}` : ''}</p>
        <p class="link">REFERÊNCIA: <span>${refLine}</span></p>
        <p class="author key">Tom: <span id="song-key">${songData.key} ${keyAccumulationLabel}</span></p>
        <button id="toggleChords" class="toggle-chords"><i class="fas fa-guitar"></i>${chordsVisible ? 'Ocultar' : 'Mostrar'} Acordes</button>
        <button class="toggle-share whatsapp-share" onclick="window.open('https://wa.me/?text=${encodeURIComponent(waText)}', '_blank')"><i class="fas fa-share-alt"></i> Compartilhar</button>
        ${firstVideoUrl ? `<button type="button" class="toggle-youtube"><i class="fab fa-youtube"></i> YouTube</button>` : ''}
        <button id="transposeUp" class="toggle-chords transpose-btn"><i class="fas fa-arrow-up"></i> Subir Tom</button>
        <button id="transposeDown" class="toggle-chords transpose-btn"><i class="fas fa-arrow-down"></i> Descer Tom</button>
        <button id="resetKey" class="toggle-chords transpose-btn"><i class="fas fa-undo"></i> Tom Original</button>
        <button class="toggle-print" onclick="window.print()"><i class="fas fa-print"></i> Imprimir</button>
        <button class="toggle-whatsapp-lyrics" onclick="exportLyricsToWhatsApp()" title="Exportar letra sem cifra para WhatsApp"><i class="fab fa-whatsapp"></i> Letra WhatsApp</button>
        <button class="toggle-copy-chords" onclick="shareChordChart(event)" title="Compartilhar cifras e letras"><i class="fas fa-share-alt"></i> Compartilhar Cifras</button>
    `;
    songContent.appendChild(header);

    const youtubeBtn = header.querySelector('.toggle-youtube');
    if (youtubeBtn && firstVideoUrl) {
        youtubeBtn.addEventListener('click', () => showYoutubeModal(firstVideoUrl));
    }

    // Scroll to top of page
    window.scrollTo(0, 0);

    // Add transpose button functionality
    const transposeUpBtn = header.querySelector('#transposeUp');
    const transposeDownBtn = header.querySelector('#transposeDown');
    
    // Store original key when song is loaded
    originalKey = songData.key;

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

    // Add toggle chords functionality
    const toggleChordsBtn = header.querySelector('#toggleChords');
    
    // Initialize chord visibility based on global state
    document.querySelectorAll('.chords').forEach(chord => {
        chord.style.display = chordsVisible ? 'block' : 'none';
    });

    toggleChordsBtn.addEventListener('click', () => {
        chordsVisible = !chordsVisible;
        toggleChordsBtn.innerHTML = `<i class="fas fa-guitar"></i>${chordsVisible ? 'Ocultar' : 'Mostrar'} Acordes`;
        document.querySelectorAll('.chords').forEach(chord => {
            chord.style.display = chordsVisible ? 'block' : 'none';
        });
        
        // Toggle compact-lyrics class on lyrics elements when chords are hidden
    document.querySelectorAll('.lyrics').forEach(lyric => {
            lyric.classList.toggle('compact-lyrics', !chordsVisible);
        });
        
        // LÓGICA DE ATUALIZAÇÃO DA URL MODIFICADA
        const url = new URL(window.location);
        if (chordsVisible) {
            // Se os acordes estão visíveis (padrão), removemos o parâmetro da URL
            url.searchParams.delete('chords');
        } else {
            // Se estão ocultos, definimos o parâmetro como 'false'
            url.searchParams.set('chords', 'false');
        }
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
}

/**
 * Exports lyrics only (no chords) formatted for WhatsApp.
 * Rich formatting: emojis for sections, bold title, separators, better spacing.
 */
function exportLyricsToWhatsApp() {
    if (!currentSongData || !currentSongData.chord_chart) return;

    const lines = currentSongData.chord_chart.split('\n');
    const items = []; // { type: 'heading'|'lyrics', heading?: {name, emoji}, lines?: string[] }

    lines.forEach(line => {
        const trimmed = line.trim();
        if (trimmed === '') {
            const last = items[items.length - 1];
            if (last && last.type === 'lyrics' && last.lines.length > 0) {
                last.lines.push('');
            }
            return;
        }
        if (line.startsWith('.')) return;

        const headingMatch = line.match(/^\s*\[(.*?)\]\s*$/);
        if (headingMatch) {
            const sectionName = headingMatch[1].trim().toUpperCase();
            items.push({ type: 'heading', name: sectionName });
            return;
        }

        const lyricText = line.replace(/^\s+/, '').toUpperCase();
        const last = items[items.length - 1];
        if (last && last.type === 'lyrics') {
            last.lines.push(lyricText);
        } else {
            items.push({ type: 'lyrics', lines: [lyricText] });
        }
    });

    const parts = [];

    parts.push('');
    parts.push('-'.repeat(15));
    parts.push(`MÚSICA: *${currentSongData.title.toUpperCase()}*`);
    parts.push('-'.repeat(15));
    if (currentSongData.author) parts.push(`_${currentSongData.author}_`);
    if (currentSongData.key) parts.push(`Tom: ${currentSongData.key}`);
    parts.push('');
    parts.push('');

    items.forEach(item => {
        if (item.type === 'heading') {
            parts.push(`*${item.name} ---------*`);
        } else if (item.type === 'lyrics' && item.lines && item.lines.length > 0) {
            const text = item.lines.join('\n').trim();
            if (text) {
                parts.push(text);
                parts.push('');
            }
        }
    });

    const fullText = parts.join('\n').replace(/\n{3,}/g, '\n\n').trim();
    const waUrl = `https://wa.me/?text=${encodeURIComponent(fullText)}`;
    window.open(waUrl, '_blank');
}

function copyTextWithExecCommand(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try {
        return document.execCommand('copy');
    } finally {
        document.body.removeChild(ta);
    }
}

/**
 * Shares the full chord chart (chords + lyrics) using Web Share API.
 * Falls back to clipboard copy if Web Share API is not available.
 * Formats with header (Música, Versão, Tom) and removes dots from chord lines.
 * Useful for importing into other applications on mobile devices.
 */
async function shareChordChart(event) {
    if (!currentSongData || !currentSongData.chord_chart) return;

    try {
        const lines = currentSongData.chord_chart.split('\n');
        const formattedLines = [];

        // Add header
        formattedLines.push(`Música: ${currentSongData.title}`);
        if (currentSongData.author) {
            formattedLines.push(`Versão: ${currentSongData.author}`);
        }
        if (currentSongData.key) {
            formattedLines.push(`Tom: ${currentSongData.key}`);
        }
        formattedLines.push(''); // Empty line after header

        // Process chord chart lines
        lines.forEach(line => {
            const trimmed = line.trim();
            
            if (trimmed === '') {
                formattedLines.push('');
                return;
            }

            // Remove dot from chord lines (lines starting with .)
            if (line.startsWith('.')) {
                const chordLine = line.substring(1); // Remove the dot
                formattedLines.push(chordLine);
                return;
            }

            // Keep section headings and lyrics as-is
            formattedLines.push(line);
        });

        const formattedText = formattedLines.join('\n');
        var evTarget = event && event.target;
        var button =
            (evTarget && evTarget.closest && evTarget.closest('.toggle-copy-chords')) ||
            document.querySelector('.toggle-copy-chords');
        
        // Try Web Share API first (works on mobile devices)
        if (navigator.share) {
            try {
                await navigator.share({
                    title: `${currentSongData.title} - Cifras`,
                    text: formattedText
                });
                
                // Show feedback
                if (button) {
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="fas fa-check"></i> Compartilhado!';
                    button.style.backgroundColor = '#28a745';
                    setTimeout(() => {
                        button.innerHTML = originalText;
                        button.style.backgroundColor = '';
                    }, 2000);
                }
                return;
            } catch (shareError) {
                // User cancelled share or error occurred, fall through to clipboard
                if (shareError.name === 'AbortError') {
                    return; // User cancelled, don't show error
                }
            }
        }
        
        // Fallback to clipboard copy (API moderna ou execCommand em Safari antigo)
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(formattedText);
        } else if (!copyTextWithExecCommand(formattedText)) {
            throw new Error('Clipboard indisponível');
        }
        
        // Show feedback to user
        if (button) {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i> Copiado!';
            button.style.backgroundColor = '#28a745';
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.backgroundColor = '';
            }, 2000);
        }
    } catch (err) {
        console.error('Failed to share/copy text: ', err);
        alert('Erro ao compartilhar. Tente novamente.');
    }
}

function extractYoutubeVideoId(rawUrl) {
    if (!rawUrl || typeof rawUrl !== 'string') return '';
    let s = rawUrl.trim();
    if (!s) return '';
    if (!/^https?:\/\//i.test(s)) {
        s = `https://${s}`;
    }
    let urlObj;
    try {
        urlObj = new URL(s);
    } catch (e) {
        return '';
    }
    const host = urlObj.hostname.toLowerCase();
    const parts = urlObj.pathname.split('/').filter(Boolean);

    if (host === 'youtu.be' || host.endsWith('.youtu.be')) {
        const id = parts[0] || '';
        return id.split('?')[0] || '';
    }

    if (host.includes('youtube.com') || host.includes('youtube-nocookie.com')) {
        const v = urlObj.searchParams.get('v');
        if (v) return v;
        const seg = parts[0];
        if ((seg === 'embed' || seg === 'shorts' || seg === 'live' || seg === 'v') && parts[1]) {
            return parts[1].split('?')[0];
        }
    }
    return '';
}

// Function to show YouTube modal
function showYoutubeModal(url) {
    const urlObj = (() => {
        let s = (url || '').trim();
        if (!s) return null;
        if (!/^https?:\/\//i.test(s)) s = `https://${s}`;
        try {
            return new URL(s);
        } catch (e) {
            return null;
        }
    })();

    const videoId = extractYoutubeVideoId(url);
    if (!videoId) {
        if (url && /^https?:\/\//i.test(url.trim())) {
            window.open(url.trim(), '_blank', 'noopener,noreferrer');
        }
        return;
    }

    const tParam =
        urlObj &&
        (urlObj.searchParams.get('t') ||
            urlObj.searchParams.get('start') ||
            urlObj.searchParams.get('time_continue'));
    const startSeconds = tParam ? String(tParam).replace(/[^0-9]/g, '') : '';

    const container = document.getElementById('youtube-container');
    suspendFiltersForYoutubeEmbed();

    const embedQs = ['playsinline=1', 'rel=0', 'modestbranding=1'];
    if (startSeconds) {
        embedQs.unshift('start=' + encodeURIComponent(startSeconds));
    }
    const embedSrc =
        'https://www.youtube.com/embed/' +
        encodeURIComponent(videoId) +
        '?' +
        embedQs.join('&');

    container.innerHTML = '';
    const iframe = document.createElement('iframe');
    iframe.width = 320;
    iframe.height = 180;
    iframe.setAttribute('frameborder', '0');
    iframe.setAttribute('allowfullscreen', 'allowfullscreen');
    iframe.setAttribute('webkitallowfullscreen', 'webkitallowfullscreen');
    iframe.setAttribute('mozallowfullscreen', 'mozallowfullscreen');
    iframe.src = embedSrc;
    container.appendChild(iframe);

    const modal = document.getElementById('youtubeModal');
    modal.style.display = 'block';

    function closeYoutubeModal() {
        modal.style.display = 'none';
        container.innerHTML = '';
        restoreYoutubeModalFilters();
    }

    const closeBtn = modal.querySelector('.close-button');
    closeBtn.onclick = function () {
        closeYoutubeModal();
    };

    window.onclick = function (event) {
        if (event.target === modal) {
            closeYoutubeModal();
        }
    };
}