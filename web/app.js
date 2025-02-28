let allSongs = [];

async function loadAllSongs() {

    try {
        const response = await fetch('../songs/');
        const files = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(files, 'text/html');
        const links = Array.from(doc.querySelectorAll('a'));
        const jsonFiles = links
            .map(link => link.getAttribute('href'))
            .filter(href => href && href.endsWith('.json'));

        const songPromises = jsonFiles.map(async file => {
            const response = await fetch(`../${file}`);
            return await response.json();
        });

        allSongs = await Promise.all(songPromises);
        setupSearch();
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
            song.author.toLowerCase().includes(query)
        );

        displaySearchResults(filteredSongs);
    });
}

function displaySearchResults(songs) {
    const searchResults = document.getElementById('searchResults');
    searchResults.innerHTML = '';
    searchResults.style.display = songs.length ? 'block' : 'none';

    songs.forEach(song => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        resultItem.innerHTML = `
            <strong>${song.title}</strong>
            ${song.author ? `<br>by ${song.author}` : ''}
            ${song.key ? `<br>Key: ${song.key}` : ''}
        `;
        resultItem.addEventListener('click', () => {
            createSongContent(song);
            searchResults.style.display = 'none';
            document.getElementById('searchInput').value = '';
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
    songContent.style.display = 'block';
    songContent.style.visibility = 'visible';
    songContent.style.position = 'relative';
    songContent.style.overflow = 'visible';
    
    // Create song header
    const header = document.createElement('div');
    header.innerHTML = `
        <h1>${songData.title}</h1>
        <p class="author">${songData.author}</p>
        <p class="key">Tom: <span>${songData.key}</span></p>
    `;
    songContent.appendChild(header);

    // Create chord chart content
    const chordChart = document.createElement('div');
    chordChart.className = 'chord-chart';
    
    const lines = songData.chord_chart.split('\n');
    lines.forEach(line => {
        const lineElement = document.createElement('div');
        
        if (line.trim() === '') {
            lineElement.className = 'empty-line';
            lineElement.innerHTML = '&nbsp;';
        } else if (line.match(/^\[.*\]$/)) {
            lineElement.className = 'section-header';
            lineElement.textContent = line.toUpperCase();
        } else if (line.startsWith('.')) {
            lineElement.className = 'chord-line';
            lineElement.textContent = line.substring(1);
        } else {
            lineElement.className = 'lyric-line';
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