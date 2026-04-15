let allSongsData = {};
let allSetsData = [];
let topWordsData = [];
const SINGERS = ['Geraldo', 'Eric', 'Theo', 'Daniel', 'Pompeu'];

function songLookup(songId) {
    const k = String(songId);
    return allSongsData[k] || allSongsData[songId];
}

function parseDate(dateStr) {
    const [day, month, year] = dateStr.split('/');
    return new Date(year, month - 1, day);
}

function updateDashboard() {
    const startDate = new Date(document.getElementById('startDate').value + 'T00:00:00');
    const endDate = new Date(document.getElementById('endDate').value + 'T00:00:00');

    const filteredSets = allSetsData.filter(set => {
        const setDate = parseDate(set.date);
        return setDate >= startDate && setDate <= endDate;
    });

    let totalSongsUsed = 0;
    filteredSets.forEach(set => (totalSongsUsed += (set.songs || []).length));

    if (filteredSets.length > 0) {
        filteredSets.sort((a, b) => parseDate(a.date) - parseDate(b.date));
        document.getElementById('periodoAnalisado').innerText =
            parseDate(filteredSets[0].date).toLocaleDateString('pt-BR') +
            ' a ' +
            parseDate(filteredSets[filteredSets.length - 1].date).toLocaleDateString('pt-BR');
    } else {
        document.getElementById('periodoAnalisado').innerText = 'Nenhum dado no período';
    }

    document.getElementById('totalSets').innerText = filteredSets.length;
    document.getElementById('totalSongsUsed').innerText = totalSongsUsed;
    document.getElementById('mediaMusicas').innerText =
        filteredSets.length > 0 ? Math.round(totalSongsUsed / filteredSets.length) : 0;

    const allSongsInSets = [],
        allAuthorsInSets = [],
        allFirstSongsInSets = [],
        allLastSongsInSets = [];
    const offeringSongs = [],
        breadSongs = [],
        wineSongs = [];
    const singersCount = new Counter();
    const singerSongKeys = {};
    const singerTopSongs = {};
    const weatherBySinger = {};

    SINGERS.forEach(s => {
        singerSongKeys[s] = new Counter();
        singerTopSongs[s] = new Counter();
        weatherBySinger[s] = { rain: 0, no_rain: 0 };
    });

    filteredSets.forEach(set => {
        const title = set.title || '';
        const songsInSet = set.songs || [];
        const currentSinger = SINGERS.find(s => title.toUpperCase().includes(s.toUpperCase()));

        if (currentSinger) {
            singersCount.add(currentSinger);
            if (set.it_rained) {
                weatherBySinger[currentSinger].rain += 1;
            } else {
                weatherBySinger[currentSinger].no_rain += 1;
            }
        }

        if (songsInSet.length > 0) {
            allFirstSongsInSets.push(songsInSet[0].song_id);
            allLastSongsInSets.push(songsInSet[songsInSet.length - 1].song_id);
        }

        songsInSet.forEach(song => {
            const songData = songLookup(song.song_id);
            if (songData) {
                const songTitle = songData.title;
                allSongsInSets.push(songTitle);
                if (songData.author) allAuthorsInSets.push(songData.author);
                if (song.notes) {
                    if (song.notes.includes('Oferta')) offeringSongs.push(songTitle);
                    if (song.notes.includes('Pão')) breadSongs.push(songTitle);
                    if (song.notes.includes('Cálice')) wineSongs.push(songTitle);
                }
                if (currentSinger && song.key) {
                    let key = song.key.split(' ')[0];
                    if (['A#', 'Bb'].includes(key)) key = 'A# / Bb';
                    else if (['G#', 'Ab'].includes(key)) key = 'G# / Ab';
                    else if (['C#', 'Db'].includes(key)) key = 'C# / Db';
                    else if (['F#', 'Gb'].includes(key)) key = 'F# / Gb';
                    singerSongKeys[currentSinger].add(key);
                    singerTopSongs[currentSinger].add(songTitle);
                }
            }
        });
    });

    const createChartData = (counter, topN) => {
        const mostCommon = counter.mostCommon(topN);
        return {
            labels: mostCommon.map(item => item[0]),
            data: mostCommon.map(item => item[1])
        };
    };

    const getSongTitles = ids =>
        ids.map(id => {
            const row = songLookup(id);
            return row ? row.title : 'Desconhecido';
        });

    updateBarChart('topSongsChart', createChartData(new Counter(allSongsInSets), 10), 'rgba(153, 102, 255, 0.6)');
    updateBarChart('topAuthorsChart', createChartData(new Counter(allAuthorsInSets), 10), 'rgba(255, 99, 132, 0.6)');
    updateBarChart('firstSongsChart', createChartData(new Counter(getSongTitles(allFirstSongsInSets)), 10), 'rgba(255, 99, 132, 0.6)');
    updateBarChart('lastSongsChart', createChartData(new Counter(getSongTitles(allLastSongsInSets)), 10), 'rgba(54, 162, 235, 0.6)');
    updateBarChart('offeringSongsChart', createChartData(new Counter(offeringSongs), 10), 'rgba(255, 159, 64, 0.6)');
    updateBarChart('breadSongsChart', createChartData(new Counter(breadSongs), 10), 'rgba(75, 192, 192, 0.6)');
    updateBarChart('wineSongsChart', createChartData(new Counter(wineSongs), 10), 'rgba(153, 102, 255, 0.6)');
    updateBarChart('singersChart', createChartData(singersCount, 10), 'rgba(75, 192, 192, 0.6)');
    updateRadarChart('singerKeysChart', singerSongKeys);
    updateSingerTopSongsCharts(singerTopSongs);
    updateWeatherChart('weatherBySingerChart', weatherBySinger);
}

function updateBarChart(canvasId, chartData, color) {
    if (window[canvasId + '_chart']) window[canvasId + '_chart'].destroy();
    const ctx = document.getElementById(canvasId).getContext('2d');
    window[canvasId + '_chart'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{ label: 'Quantidade', data: chartData.data, backgroundColor: color }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: {
                datalabels: { anchor: 'end', align: 'start', formatter: v => (v > 0 ? v : '') },
                legend: { display: false }
            },
            scales: { x: { beginAtZero: true } }
        }
    });
}

function updateRadarChart(canvasId, singerKeysData) {
    if (window.singerKeysChartInstance) window.singerKeysChartInstance.destroy();
    const allKeys = [
        ...new Set(Object.values(singerKeysData).flatMap(counter => Object.keys(counter.counts)))
    ].sort();
    const datasets = SINGERS.map((singer, index) => {
        const colors = [
            'rgba(255, 99, 132, 0.4)',
            'rgba(54, 162, 235, 0.4)',
            'rgba(255, 206, 86, 0.4)',
            'rgba(75, 192, 192, 0.4)',
            'rgba(153, 102, 255, 0.4)',
            'rgba(255, 159, 64, 0.4)'
        ];
        const color = colors[index % colors.length];
        return {
            label: singer,
            data: allKeys.map(key => singerKeysData[singer].get(key)),
            backgroundColor: color,
            borderColor: color.replace('0.4', '1'),
            borderWidth: 1
        };
    });
    const ctx = document.getElementById(canvasId).getContext('2d');
    window.singerKeysChartInstance = new Chart(ctx, {
        type: 'radar',
        data: { labels: allKeys, datasets: datasets },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function updateSingerTopSongsCharts(singerTopSongs) {
    const container = document.getElementById('singerTopSongsChartsContainer');
    container.innerHTML = '';
    SINGERS.forEach(singer => {
        const topSongs = singerTopSongs[singer].mostCommon(10);
        if (topSongs.length > 0) {
            const chartContainer = document.createElement('div');
            chartContainer.className = 'singer-top-songs-chart';
            chartContainer.innerHTML = '<h3>' + singer + '</h3><canvas id="singerTopSongs_' + singer + '"></canvas>';
            container.appendChild(chartContainer);
            updateBarChart(
                'singerTopSongs_' + singer,
                { labels: topSongs.map(s => s[0]), data: topSongs.map(s => s[1]) },
                'rgba(75, 192, 192, 0.6)'
            );
        }
    });
}

function updateWeatherChart(canvasId, weatherData) {
    if (window.weatherChartInstance) window.weatherChartInstance.destroy();
    const labels = Object.keys(weatherData).filter(s => weatherData[s].rain > 0 || weatherData[s].no_rain > 0);
    const rainData = labels.map(singer => weatherData[singer]['rain']);
    const noRainData = labels.map(singer => weatherData[singer]['no_rain']);

    const ctx = document.getElementById(canvasId).getContext('2d');
    window.weatherChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: 'Choveu', data: rainData, backgroundColor: 'rgba(75, 192, 192, 0.6)' },
                { label: 'Não Choveu', data: noRainData, backgroundColor: 'rgba(255, 99, 132, 0.6)' }
            ]
        },
        options: {
            responsive: true,
            scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } },
            plugins: { datalabels: { formatter: v => (v > 0 ? v : '') } }
        }
    });
}

class Counter {
    constructor(initial = []) {
        this.counts = {};
        initial.forEach(item => this.add(item));
    }
    add(item) {
        this.counts[item] = (this.counts[item] || 0) + 1;
    }
    get(item) {
        return this.counts[item] || 0;
    }
    mostCommon(n) {
        return Object.entries(this.counts)
            .sort(([, a], [, b]) => b - a)
            .slice(0, n);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    Chart.register(ChartDataLabels);

    const regEl = document.getElementById('totalSongsRegistered');
    try {
        const d = await loadRelatorioDatasetsFromEigreja();
        allSongsData = d.allSongsData;
        allSetsData = d.allSetsData;
        topWordsData = d.topWordsData;
        if (regEl) regEl.textContent = Object.keys(allSongsData).length;
    } catch (e) {
        console.error(e);
        if (regEl) regEl.textContent = '—';
        document.body.insertAdjacentHTML(
            'afterbegin',
            '<div style="padding:12px;background:#fee;color:#800;">Não foi possível carregar dados do eIgreja. Defina o slug em eigreja-config.js ou use ?church= na URL. ' +
                (e.message || '') +
                '</div>'
        );
        return;
    }

    document.getElementById('filterButton').addEventListener('click', updateDashboard);

    const wordCloudCtx = document.getElementById('wordCloudChart').getContext('2d');
    new Chart(wordCloudCtx, {
        type: 'wordCloud',
        data: {
            labels: topWordsData.map(item => item[0]),
            datasets: [
                {
                    label: '',
                    data: topWordsData.map(item => item[1] / 2.5)
                }
            ]
        },
        options: {
            title: {
                display: true,
                text: 'Chart.js Word Cloud'
            },
            plugins: {
                legend: { display: false },
                datalabels: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const originalValue = topWordsData[context.dataIndex][1];
                            return context.label + ': ' + originalValue;
                        }
                    }
                }
            },
            font: {
                weight: 'normal',
                min: 5,
                max: 20
            }
        }
    });

    updateDashboard();
});
