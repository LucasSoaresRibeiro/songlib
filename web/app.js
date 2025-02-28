window.jsPDF = window.jspdf.jsPDF;

async function loadSongData() {
    try {
        const response = await fetch('../songs/85049.json');
        const songData = await response.json();
        generatePDF(songData);
    } catch (error) {
        console.error('Error loading song data:', error);
    }
}

function generatePDF(songData) {
    const doc = new jsPDF({
        format: 'a4',
        unit: 'mm',
        putOnlyUsedFonts: true
    });

    // Set initial position
    let yPosition = 15;
    const margin = 15;
    const lineHeight = 7;
    const pageHeight = doc.internal.pageSize.height;

    // Title
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(24);
    doc.setTextColor('#0675bc');
    doc.text(songData.title.toUpperCase(), margin, yPosition);
    yPosition += lineHeight * 2;

    // Author
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(12);
    doc.setTextColor('#7e7e7e');
    doc.text(`${songData.author}`, margin, yPosition);
    yPosition += lineHeight * 1.5;

    // Key and Reference
    doc.setFontSize(12);
    doc.text(`Tom: `, margin, yPosition);
    doc.setTextColor('#0675bc');
    doc.setFont('helvetica', 'bold');
    doc.text(songData.key, margin + 10, yPosition);
    yPosition += lineHeight * 2;

    // Format and display chord chart
    doc.setFontSize(11);
    const chordLines = songData.chord_chart.split('\n');
    
    chordLines.forEach(line => {
        // Skip empty lines
        if (line.trim() === '') {
            yPosition += lineHeight;
            return;
        }

        // Check if we need a new page
        if (yPosition > pageHeight - 20) {
            doc.addPage();
            yPosition = 20;
        }

        // Handle section headers [A], [B], etc.
        if (line.match(/^\[.*\]$/)) {
            doc.setFillColor('#fd8000');
            doc.setTextColor('#ffffff');
            doc.setFont('helvetica', 'bold');
            const sectionText = line.toUpperCase();
            const textWidth = doc.getTextWidth(sectionText);
            doc.rect(margin - 1, yPosition - 4, textWidth + 8, 6, 'F');
            doc.text(sectionText, margin + 3, yPosition);
            doc.setTextColor('#000000');
        } else {
            // Handle chord lines (starting with dots)
            if (line.startsWith('.')) {
                doc.setFont('helvetica', 'bold');
                doc.setTextColor('#0675bc');
                doc.text(line.substring(1), margin + 5, yPosition);
            } else {
                // Handle lyrics
                doc.setFont('helvetica', 'normal');
                doc.setTextColor('#000000');
                doc.text(line.toUpperCase(), margin + 5, yPosition);
            }
        }
        yPosition += lineHeight;
    });

    // Display the PDF
    const pdfDataUri = doc.output('datauristring');
    const pdfContainer = document.getElementById('pdfContainer');
    pdfContainer.innerHTML = `<embed src="${pdfDataUri}" type="application/pdf" width="100%" height="100%">`;
}

// Load song data when the page loads
document.addEventListener('DOMContentLoaded', loadSongData);