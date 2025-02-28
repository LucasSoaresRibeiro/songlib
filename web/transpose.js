// ChordSheetJS library for chord transposition
// import { ChordSheetJS } from 'chordsheetjs';

window.SongTransposer = class SongTransposer {
    constructor() {
        this.parser = new ChordSheetJS.ChordProParser();
        this.formatter = new ChordSheetJS.HtmlDivFormatter();
        this.setupTransposeControls();
    }

    setupTransposeControls() {
        // Create transpose select element for each song
        document.querySelectorAll('.chordchart').forEach(chartElement => {
            const transposeSelect = this.createTransposeSelect();
            chartElement.insertBefore(transposeSelect, chartElement.firstChild);

            // Store original chord content
            const originalContent = chartElement.innerHTML;
            chartElement.dataset.originalContent = originalContent;

            transposeSelect.addEventListener('change', (e) => {
                const semitones = parseInt(e.target.value);
                this.transposeSong(chartElement, semitones);
            });
        });
    }

    createTransposeSelect() {
        const container = document.createElement('div');
        container.className = 'transpose-container';

        const select = document.createElement('select');
        select.className = 'transpose-select';

        // Add transpose options from -6 to +6 semitones
        for (let i = -6; i <= 6; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.text = i === 0 ? 'Original Key' : (i > 0 ? `+${i}` : i);
            select.appendChild(option);
        }

        const label = document.createElement('label');
        label.textContent = 'Transpose: ';
        label.appendChild(select);

        container.appendChild(label);
        return container;
    }

    transposeSong(chartElement, semitones) {
        if (semitones === 0) {
            // Reset to original content
            chartElement.innerHTML = chartElement.dataset.originalContent;
            return;
        }

        // Extract chord lines
        const chordLines = chartElement.querySelectorAll('.chords');
        chordLines.forEach(line => {
            const chords = line.textContent.trim().split(/\s+/);
            const transposedChords = chords.map(chord => this.transposeChord(chord, semitones));
            line.textContent = transposedChords.join(' ');
        });
    }

    transposeChord(chord, semitones) {
        const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
        const flatNotes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
        const chordPattern = /^([A-G][#b]?)(.*)/;
        const match = chord.match(chordPattern);

        if (!match) return chord;

        const [, note, suffix] = match;
        // Handle both sharp and flat notes
        const isFlat = note.includes('b');
        const noteArray = isFlat ? flatNotes : notes;
        const cleanNote = note.replace('b', '');
        
        let currentIndex = noteArray.indexOf(cleanNote);
        if (currentIndex === -1) {
            // Try the alternative notation
            const altNoteArray = isFlat ? notes : flatNotes;
            const altIndex = altNoteArray.indexOf(cleanNote);
            if (altIndex === -1) return chord;
            currentIndex = altIndex;
        }

        const newIndex = (currentIndex + semitones + 12) % 12;
        return (isFlat ? flatNotes[newIndex] : notes[newIndex]) + suffix;
    }
}

// Initialize transposer when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SongTransposer();
});