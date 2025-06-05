function transpose(direction) {
    const parser = new ChordSheetJS.ChordsOverWordsParser();
    const formatter = new ChordSheetJS.TextFormatter();

    let chordChart;
    
    if (!currentSongData['chord_chart_original']) {
        chordChart = currentSongData['chord_chart'];
        currentSongData['chord_chart_original'] = chordChart;
        currentSongData['key_original'] = currentSongData['key'];
        currentSongData['key_accumulation'] = direction === 'up' ? 1 : -1;
    } else {
        chordChart = currentSongData['chord_chart_original'];
        currentSongData['key_accumulation'] = direction === 'up' ? ++currentSongData['key_accumulation'] : --currentSongData['key_accumulation'];
    }
    // console.log(currentSongData['key_accumulation']);
    const lines = chordChart.split('\n');
    
    const transposedLines = lines.map(line => {
        if (line.startsWith('.')) {
            // Get leading spaces before the first chord
            const leadingSpaces = line.match(/^\.s*/)[0].substring(1);
            // Remove the dot prefix and leading spaces for parsing
            const chordLine = line.substring(leadingSpaces.length + 1);
            // Split the chord line by spaces while preserving original spacing
            const chordSegments = chordLine.split(/(?<=\s)(?=\S)/); // Split between whitespace and non-whitespace
            
            // Process each chord segment
            const transposedSegments = chordSegments.map(segment => {
                const chord = segment.trim();
                const originalSpacing = segment.match(/\s*$/)[0];
                
                if (!chord) return originalSpacing; // Return original spacing for empty segments

                // Skip transposition if chord contains only numbers and special characters
                if (/^[0-9+\-\s]*$/.test(chord)) {
                    return chord + originalSpacing;
                }

                // Handle complex chord notations
                let processedChord = chord;
                
                // Extract numeric modifiers (like '5+') and preserve them
                const numericModifier = processedChord.match(/([0-9]+\+?)$/)?.[0] || '';
                processedChord = processedChord.replace(/[0-9]+\+?$/, '');
                
                // Extract additional chord information
                const chordMatch = processedChord.match(/^([A-G][b#]?)(.*)$/);
                let baseChord = processedChord;
                let chordSuffix = '';
                let bassNote = '';

                if (chordMatch) {
                    baseChord = chordMatch[1];
                    chordSuffix = chordMatch[2];
                }
                
                // Handle bass note
                if (processedChord.includes('/')) {
                    const [chordWithSuffix, bassNote] = processedChord.split('/');
                    
                    // Extract base chord and suffix before the slash
                    const baseMatch = chordWithSuffix.match(/^([A-G][b#]?)(.*)$/);
                    if (baseMatch) {
                        baseChord = baseMatch[1];
                        chordSuffix = baseMatch[2];
                    }

                    // Process base chord with suffix
                    let chordData = parser.parse(baseChord);
                    let transposedBase = chordData.transpose(currentSongData['key_accumulation']);
                    transposedBase.useModifier('#');
                    let formattedChord = formatter.format(transposedBase) + chordSuffix;

                    // Process bass note
                    chordData = parser.parse(bassNote);
                    let transposedBass = chordData.transpose(currentSongData['key_accumulation']);
                    transposedBass.useModifier('#');
                    formattedChord += '/' + formatter.format(transposedBass);

                    // Add numeric modifier if present and adjust spacing
                    let transposedChord = numericModifier ? formattedChord + numericModifier : formattedChord;
                    // Calculate length difference and adjust spacing
                    const lengthDiff = chord.length - transposedChord.length;
                    let adjustedSpacing = lengthDiff > 0 ? originalSpacing + ' '.repeat(Math.max(0, lengthDiff)) : originalSpacing.substring(0, originalSpacing.length+lengthDiff);
                    adjustedSpacing = adjustedSpacing == '' ? ' ' : adjustedSpacing;
                    return transposedChord + adjustedSpacing;
                }

                // Process regular chord
                let chordData = parser.parse(baseChord);
                let transposedBase = chordData.transpose(currentSongData['key_accumulation']);
                transposedBase.useModifier('#');
                let formattedChord = formatter.format(transposedBase) + chordSuffix;
                formattedChord = numericModifier ? formattedChord + numericModifier : formattedChord;
                // Calculate length difference and adjust spacing
                const lengthDiff = chord.length - formattedChord.length;
                let adjustedSpacing = lengthDiff > 0 ? originalSpacing + ' '.repeat(Math.max(0, lengthDiff)) : originalSpacing.substring(0, originalSpacing.length+lengthDiff);
                adjustedSpacing = adjustedSpacing == '' ? ' ' : adjustedSpacing;
                return formattedChord + adjustedSpacing;
            });
            
            // Join the segments and add the dot prefix with original leading spaces
            return '.' + leadingSpaces + transposedSegments.join('');
        }
        return line; // Return non-chord lines unchanged
    });
    
    const transposedChart = transposedLines.join('\n');
    currentSongData['chord_chart'] = transposedChart;
    currentSongData['key'] = direction === 'up' ? formatter.format(parser.parse(currentSongData['key']).transposeUp()): formatter.format(parser.parse(currentSongData['key']).transposeDown());

    const isTranposed = true;
    createSongContent(currentSongData, isTranposed);
}