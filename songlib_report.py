import json
import os
from collections import Counter, defaultdict
import requests
from datetime import datetime
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

# Open-Meteo Historical Weather API configuration
WEATHER_API_URL = "https://archive-api-open-meteo.com/v1/era5"
DEFAULT_LATITUDE = -23.2701002  # IBM latitude
DEFAULT_LONGITUDE = -45.8214431 # IBM longitude

SETS_DIR = 'c:\\Lucas\\Repos\\pessoal\\github\\songlib\\sets'
SONGS_DIR = 'c:\\Lucas\\Repos\\pessoal\\github\\songlib\\songs'
SINGERS = {
    "Geraldo": 0,
    "Eric": 0,
    # "Amanda": 0,
    "Theo": 0,
    "Daniel": 0,
    "Pompeu": 0,
}

# Arquivo para o cache local de dados de clima
WEATHER_CACHE_FILE = 'weather_cache.json'

def get_weather_data(date_str, latitude, longitude):
    """Faz a chamada à API de clima para uma data específica."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date_str,
        "end_date": date_str,
        "hourly": "precipitation",
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if "hourly" in data and "precipitation" in data["hourly"]:
            for precip in data["hourly"]["precipitation"]:
                if precip is not None and precip > .15:
                    return True  # Choveu
        return False  # Não choveu
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data for {date_str}: {e}")
        return False

def generate_report():
    all_songs_data = {}
    for filename in os.listdir(SONGS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(SONGS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                song_data = json.load(f)
                song_id = filename.split('.')[0]
                all_songs_data[song_id] = song_data

    # --- LÓGICA DE CACHE DE CLIMA ---
    weather_cache = {}
    try:
        with open(WEATHER_CACHE_FILE, 'r', encoding='utf-8') as f:
            weather_cache = json.load(f)
        print(f"Cache de clima '{WEATHER_CACHE_FILE}' carregado com {len(weather_cache)} registros.")
    except FileNotFoundError:
        print(f"Arquivo de cache de clima '{WEATHER_CACHE_FILE}' não encontrado. Um novo será criado.")
    except json.JSONDecodeError:
        print(f"Erro ao ler o arquivo de cache '{WEATHER_CACHE_FILE}'. Começando com um cache vazio.")

    cache_updated = False
    all_sets_data = []
    
    set_files = [f for f in os.listdir(SETS_DIR) if f.endswith('.json')]
    total_set_files = len(set_files)
    print(f"Processando {total_set_files} arquivos de cultos...")

    for index, filename in enumerate(set_files):
        filepath = os.path.join(SETS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            set_data = json.load(f)
            
            it_rained = False
            if 'date' in set_data:
                date_obj = datetime.strptime(set_data['date'], "%d/%m/%Y")
                date_str_api = date_obj.strftime("%Y-%m-%d")
                
                if date_str_api in weather_cache:
                    it_rained = weather_cache[date_str_api]
                    print(f"({index + 1}/{total_set_files}) Clima para {date_str_api} encontrado no cache.")
                else:
                    print(f"({index + 1}/{total_set_files}) Buscando novo dado de clima para {date_str_api}...")
                    it_rained = get_weather_data(date_str_api, DEFAULT_LATITUDE, DEFAULT_LONGITUDE)
                    weather_cache[date_str_api] = it_rained
                    cache_updated = True
            
            set_data['it_rained'] = it_rained
            all_sets_data.append(set_data)

    if cache_updated:
        with open(WEATHER_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(weather_cache, f, indent=4)
        print(f"Cache de clima foi atualizado e salvo em '{WEATHER_CACHE_FILE}'.")
    else:
        print("Nenhum novo dado de clima foi buscado. O cache não precisou ser atualizado.")

    # --- FIM DA LÓGICA DE CACHE ---

    all_sets_data.sort(key=lambda x: datetime.strptime(x['date'], "%d/%m/%Y"))
    
    min_date_str = ""
    max_date_str = ""
    if all_sets_data:
        min_date = datetime.strptime(all_sets_data[0]['date'], "%d/%m/%Y")
        max_date = datetime.strptime(all_sets_data[-1]['date'], "%d/%m/%Y")
        min_date_str = min_date.strftime("%Y-%m-%d")
        max_date_str = max_date.strftime("%Y-%m-%d")

    word_counts = Counter()
    stop_words = set(stopwords.words('portuguese'))
    custom_stop_words = {'pra','intro', 'refrão', 'fim', 'verso', 'ponte', 'pre', 'solo', 'final', 'bis', 'volta', 'parte', 'coda', 'tag', 'adlib', 'interludio', 'instrumental', 'outro', 'fade', 'in', 'out', 'repeat', 'x', '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x', '10x', 'etc', 'e', 'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'sem', 'sobre', 'sob', 'entre', 'até', 'após', 'ante', 'contra', 'desde', 'durante', 'mediante', 'perante', 'segundo', 'salvo', 'tirante', 'trás', 'através', 'afora', 'dentro', 'fora', 'perto', 'longe', 'abaixo', 'acima', 'adiante', 'atrás', 'defronte', 'depois', 'diante', 'embaixo', 'emcima', 'enfim', 'então', 'logo', 'mais', 'menos', 'muito', 'pouco', 'quase', 'sempre', 'tarde', 'cedo', 'nunca', 'jamais', 'agora', 'ainda', 'já', 'ontem', 'hoje', 'amanhã', 'aqui', 'ali', 'aí', 'cá', 'lá', 'além', 'aquém', 'onde', 'aonde', 'donde', 'para onde', 'como', 'assim', 'bem', 'mal', 'melhor', 'pior', 'devagar', 'depressa', 'grátis', 'junto', 'separado', 'só', 'somente', 'apenas', 'inclusive', 'exclusivamente', 'certamente', 'provavelmente', 'talvez', 'sim', 'não', 'claro', 'decerto', 'realmente', 'verdadeiramente', 'aparentemente', 'possivelmente', 'quissá', 'acaso', 'porventura', 'talvez', 'se', 'embora', 'conforme', 'como', 'enquanto', 'quando', 'apenas', 'mal', 'assim que', 'logo que', 'desde que', 'até que', 'para que', 'a fim de que', 'porque', 'pois', 'porquanto', 'como', 'já que', 'visto que', 'uma vez que', 'seja', 'ou', 'nem', 'mas', 'porém', 'contudo', 'todavia', 'entretanto', 'no entanto', 'portanto', 'logo', 'por conseguinte', 'consequentemente', 'assim', 'destarte', 'desse modo', 'dessa forma', 'à medida que', 'à proporção que', 'quanto mais', 'quanto menos', 'quanto maior', 'quanto menor', 'que', 'se', 'como', 'conforme', 'segundo', 'consoante', 'assim como', 'bem como', 'tanto quanto', 'mais que', 'menos que', 'tão quanto', 'tão como', 'tal qual', 'qual', 'que', 'cujo', 'cuja', 'cujos', 'cujas', 'onde', 'quando', 'como', 'quanto', 'por que', 'para que', 'se', 'caso', 'contanto que', 'desde que', 'a menos que', 'exceto se', 'salvo se', 'sem que', 'dado que', 'posto que', 'uma vez que', 'ainda que', 'embora', 'conquanto', 'posto que', 'se bem que', 'mesmo que', 'por mais que', 'por menos que', 'apesar de que', 'não obstante'}
    stop_words.update(custom_stop_words)

    for song_id, song_data in all_songs_data.items():
        if 'chord_chart' in song_data and song_data['chord_chart']:
            lyrics_block = song_data['chord_chart']
            cleaned_lyrics = []
            for line in lyrics_block.split('\n'):
                if not (line.strip().startswith('.') or '|' in line or '[' in line or '(' in line or '{' in line or any(char.isdigit() for char in line)):
                    cleaned_lyrics.append(line)
            text = ' '.join(cleaned_lyrics)
            text = re.sub(r'[\W_]+', ' ', text).lower()
            words = text.split()
            filtered_words = [word.upper() for word in words if word not in stop_words and len(word) > 1]
            word_counts.update(filtered_words)
    
    top_words = word_counts.most_common(100)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>IBM - Estatísticas do Louvor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="web/style/styles-report.css">
        <link href="https://fonts.googleapis.com/css2?family=Martian+Mono:wdth,wght@87.5,100..800&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,100..700;1,100..700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
        <script src="https://unpkg.com/chartjs-chart-wordcloud@4.4.4/build/index.umd.min.js"></script>
        
        <style>
            @media print {{
                /* Define o tamanho da página e a orientação */
                @page {{
                    size: A5 landscape;
                    margin: 1cm;
                }}

                /* Garante que as cores dos gráficos sejam impressas */
                body {{
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}

                /* Oculta os containers do filtro e do logo */
                .filter-container, .logo-container {{
                    display: none;
                }}

                /* Força uma quebra de página antes do container do gráfico de precipitação */
                .weather-chart-container {{
                    page-break-before: always;
                    padding-top: 1cm; /* Adiciona um espaço no topo da nova página */
                }}
            }}
        </style>
    </head>
    <body>
        <div class="logo-container">
            <img src="images/logo.png" alt="Maranata Logo" class="logo" />
        </div>
        <h1>Estatísticas do Ministério de Louvor</h1>

        <div class="container filter-container">
            <h2>Filtro por Período</h2>
            <div class="filter-controls">
                <label for="startDate">Data Inicial:</label>
                <input type="date" id="startDate" name="startDate" value="{min_date_str}">
                <label for="endDate">Data Final:</label>
                <input type="date" id="endDate" name="endDate" value="{max_date_str}">
                <button id="filterButton">Filtrar</button>
            </div>
        </div>

        <div class="container">
            <h2>Filtro por Período</h2>
            <div class="filter-container">
                <label for="startDate">Data Inicial:</label>
                <input type="date" id="startDate" name="startDate" value="{min_date_str}">
                <label for="endDate">Data Final:</label>
                <input type="date" id="endDate" name="endDate" value="{max_date_str}">
                <button id="filterButton">Filtrar</button>
            </div>
        </div>

        <div class="container">
            <h2>Resumo:</h2>
            <div class="dashboard-container">
                <div class="dashboard-block">
                    <div class="dashboard-block-title">Período Analisado</div>
                    <div class="dashboard-block-value" id="periodoAnalisado"></div>
                </div>
                <div class="dashboard-block">
                    <div class="dashboard-block-title">Músicas Cadastradas</div>
                    <div class="dashboard-block-value">{len(all_songs_data)}</div>
                </div>
                <div class="dashboard-block">
                    <div class="dashboard-block-title">Cultos e Programações</div>
                    <div class="dashboard-block-value" id="totalSets"></div>
                </div>
                <div class="dashboard-block">
                    <div class="dashboard-block-title">Média de Músicas por Programação</div>
                    <div class="dashboard-block-value" id="mediaMusicas"></div>
                </div>
                <div class="dashboard-block">
                    <div class="dashboard-block-title">Total de Execuções de Música</div>
                    <div class="dashboard-block-value" id="totalSongsUsed"></div>
                </div>
            </div>
        </div>

        <div class="container">
            <h2>Músicas Mais Cantadas 🔝</h2>
            <canvas id="topSongsChart"></canvas>
        </div>
        <div class="container">
            <h2>Autores/Intérpretes Mais Frequentes 🔝</h2>
            <canvas id="topAuthorsChart"></canvas>
        </div>
        <div class="container">
            <h2>Músicas Mais Escolhidas como Início do Louvor 🔝</h2>
            <canvas id="firstSongsChart"></canvas>
        </div>
        <div class="container">
            <h2>Músicas Mais Escolhidas como Final do Louvor 🔝</h2>
            <canvas id="lastSongsChart"></canvas>
        </div>
        <div class="container">
            <h2>Músicas Mais Escolhidas para Oferta 🔝</h2>
            <canvas id="offeringSongsChart"></canvas>
        </div>
        <div class="container">
            <h2>Músicas Mais Escolhidas para Pão 🥖</h2>
            <canvas id="breadSongsChart"></canvas>
        </div>
        <div class="container">
            <h2>Músicas Mais Escolhidas para Cálice 🍷</h2>
            <canvas id="wineSongsChart"></canvas>
        </div>
        <div class="container">
            <h2>Cultos por Dirigente 🎤</h2>
            <canvas id="singersChart"></canvas>
        </div>
        <div class="container-limited-height">
            <h2>Tonalidades Preferidas por Dirigente 🎵</h2>
            <canvas id="singerKeysChart"></canvas>
        </div>
        <div class="container">
            <h2>Top 10 Músicas por Dirigente 🔝</h2>
            <div id="singerTopSongsChartsContainer"></div>
        </div>
        
        <!-- Adicionada uma classe específica para a quebra de página -->
        <div class="chart-container weather-chart-container">
            <h2>Índice de Precipitação por Dirigente ⛈️</h2>
            <canvas id="weatherBySingerChart"></canvas>
        </div> -->

        <div class="container-word-cloud">
            <h2>Palavras Mais Frequentes nas Músicas 🙏</h2>
            <canvas id="wordCloudChart" style="height: 400px;"></canvas>
        </div>

        <script>
            const allSongsData = {json.dumps(all_songs_data)};
            const allSetsData = {json.dumps(all_sets_data)};
            const topWordsData = {json.dumps(top_words)};
            const SINGERS = {json.dumps(list(SINGERS.keys()))};
            
            function parseDate(dateStr) {{
                const [day, month, year] = dateStr.split('/');
                return new Date(year, month - 1, day);
            }}

            function updateDashboard() {{
                const startDate = new Date(document.getElementById('startDate').value + 'T00:00:00');
                const endDate = new Date(document.getElementById('endDate').value + 'T00:00:00');

                const filteredSets = allSetsData.filter(set => {{
                    const setDate = parseDate(set.date);
                    return setDate >= startDate && setDate <= endDate;
                }});

                let totalSongsUsed = 0;
                filteredSets.forEach(set => totalSongsUsed += (set.songs || []).length);
                
                if (filteredSets.length > 0) {{
                    filteredSets.sort((a, b) => parseDate(a.date) - parseDate(b.date));
                    document.getElementById('periodoAnalisado').innerText = parseDate(filteredSets[0].date).toLocaleDateString('pt-BR') + ' a ' + parseDate(filteredSets[filteredSets.length - 1].date).toLocaleDateString('pt-BR');
                }} else {{
                    document.getElementById('periodoAnalisado').innerText = "Nenhum dado no período";
                }}

                document.getElementById('totalSets').innerText = filteredSets.length;
                document.getElementById('totalSongsUsed').innerText = totalSongsUsed;
                document.getElementById('mediaMusicas').innerText = filteredSets.length > 0 ? Math.round(totalSongsUsed / filteredSets.length) : 0;
                
                const allSongsInSets = [], allAuthorsInSets = [], allFirstSongsInSets = [], allLastSongsInSets = [];
                const offeringSongs = [], breadSongs = [], wineSongs = [];
                const singersCount = new Counter();
                const singerSongKeys = {{}};
                const singerTopSongs = {{}};
                const weatherBySinger = {{}};

                SINGERS.forEach(s => {{
                    singerSongKeys[s] = new Counter();
                    singerTopSongs[s] = new Counter();
                    weatherBySinger[s] = {{ rain: 0, no_rain: 0 }};
                }});

                filteredSets.forEach(set => {{
                    const title = set.title || '';
                    const songsInSet = set.songs || [];
                    const currentSinger = SINGERS.find(s => title.toUpperCase().includes(s.toUpperCase()));

                    if (currentSinger) {{
                        singersCount.add(currentSinger);
                        if (set.it_rained) {{
                            weatherBySinger[currentSinger].rain += 1;
                        }} else {{
                            weatherBySinger[currentSinger].no_rain += 1;
                        }}
                    }}

                    if (songsInSet.length > 0) {{
                        allFirstSongsInSets.push(songsInSet[0].song_id);
                        allLastSongsInSets.push(songsInSet[songsInSet.length - 1].song_id);
                    }}
                    
                    songsInSet.forEach(song => {{
                        const songData = allSongsData[song.song_id];
                        if (songData) {{
                            const songTitle = songData.title;
                            allSongsInSets.push(songTitle);
                            if (songData.author) allAuthorsInSets.push(songData.author);
                            if (song.notes) {{
                                if (song.notes.includes('Oferta')) offeringSongs.push(songTitle);
                                if (song.notes.includes('Pão')) breadSongs.push(songTitle);
                                if (song.notes.includes('Cálice')) wineSongs.push(songTitle);
                            }}
                            if(currentSinger && song.key) {{
                                let key = song.key.split(" ")[0];
                                if (['A#', 'Bb'].includes(key)) key = 'A# / Bb'; else if (['G#', 'Ab'].includes(key)) key = 'G# / Ab'; else if (['C#', 'Db'].includes(key)) key = 'C# / Db'; else if (['F#', 'Gb'].includes(key)) key = 'F# / Gb';
                                singerSongKeys[currentSinger].add(key);
                                singerTopSongs[currentSinger].add(songTitle);
                            }}
                        }}
                    }});
                }});

                const createChartData = (counter, topN) => {{
                    const mostCommon = counter.mostCommon(topN);
                    return {{ labels: mostCommon.map(item => item[0]), data: mostCommon.map(item => item[1]) }};
                }};
                
                const getSongTitles = (ids) => ids.map(id => allSongsData[id] ? allSongsData[id].title : 'Desconhecido');

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
            }}

            function updateBarChart(canvasId, chartData, color) {{
                if (window[canvasId + '_chart']) window[canvasId + '_chart'].destroy();
                const ctx = document.getElementById(canvasId).getContext('2d');
                window[canvasId + '_chart'] = new Chart(ctx, {{
                    type: 'bar', data: {{ labels: chartData.labels, datasets: [{{ label: 'Quantidade', data: chartData.data, backgroundColor: color }}] }},
                    options: {{ responsive: true, indexAxis: 'y', plugins: {{ datalabels: {{ anchor: 'end', align: 'start', formatter: (v) => v > 0 ? v : '' }}, legend: {{ display: false }} }}, scales: {{ x: {{ beginAtZero: true }} }} }}
                }});
            }}
            
            function updateRadarChart(canvasId, singerKeysData) {{
                 if(window.singerKeysChartInstance) window.singerKeysChartInstance.destroy();
                 const allKeys = [...new Set(Object.values(singerKeysData).flatMap(counter => Object.keys(counter.counts)))].sort();
                 const datasets = SINGERS.map((singer, index) => {{
                     const colors = ['rgba(255, 99, 132, 0.4)', 'rgba(54, 162, 235, 0.4)', 'rgba(255, 206, 86, 0.4)', 'rgba(75, 192, 192, 0.4)', 'rgba(153, 102, 255, 0.4)', 'rgba(255, 159, 64, 0.4)'];
                     const color = colors[index % colors.length];
                     return {{ label: singer, data: allKeys.map(key => singerKeysData[singer].get(key)), backgroundColor: color, borderColor: color.replace('0.4', '1'), borderWidth: 1 }};
                 }});
                 const ctx = document.getElementById(canvasId).getContext('2d');
                 window.singerKeysChartInstance = new Chart(ctx, {{ type: 'radar', data: {{ labels: allKeys, datasets: datasets }}, options: {{ responsive: true, maintainAspectRatio: false }} }});
            }}

            function updateSingerTopSongsCharts(singerTopSongs) {{
                const container = document.getElementById('singerTopSongsChartsContainer');
                container.innerHTML = '';
                SINGERS.forEach(singer => {{
                    const topSongs = singerTopSongs[singer].mostCommon(10);
                    if (topSongs.length > 0) {{
                        const chartContainer = document.createElement('div');
                        chartContainer.className = 'singer-top-songs-chart';
                        chartContainer.innerHTML = '<h3>' + singer + '</h3><canvas id="singerTopSongs_' + singer + '"></canvas>';
                        container.appendChild(chartContainer);
                        updateBarChart('singerTopSongs_' + singer, {{ labels: topSongs.map(s => s[0]), data: topSongs.map(s => s[1]) }}, 'rgba(75, 192, 192, 0.6)');
                    }}
                }});
            }}

            function updateWeatherChart(canvasId, weatherData) {{
                if(window.weatherChartInstance) window.weatherChartInstance.destroy();
                const labels = Object.keys(weatherData).filter(s => weatherData[s].rain > 0 || weatherData[s].no_rain > 0);
                const rainData = labels.map(singer => weatherData[singer]['rain']);
                const noRainData = labels.map(singer => weatherData[singer]['no_rain']);

                const ctx = document.getElementById(canvasId).getContext('2d');
                window.weatherChartInstance = new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: labels,
                        datasets: [
                            {{ label: 'Choveu', data: rainData, backgroundColor: 'rgba(75, 192, 192, 0.6)' }},
                            {{ label: 'Não Choveu', data: noRainData, backgroundColor: 'rgba(255, 99, 132, 0.6)' }}
                        ]
                    }},
                    options: {{ responsive: true, scales: {{ x: {{ stacked: true }}, y: {{ stacked: true, beginAtZero: true }} }}, plugins: {{ datalabels: {{ formatter: (v) => v > 0 ? v : '' }} }} }}
                }});
            }}

            class Counter {{
                constructor(initial = []) {{ this.counts = {{}}; initial.forEach(item => this.add(item)); }}
                add(item) {{ this.counts[item] = (this.counts[item] || 0) + 1; }}
                get(item) {{ return this.counts[item] || 0; }}
                mostCommon(n) {{ return Object.entries(this.counts).sort(([, a], [, b]) => b - a).slice(0, n); }}
            }}
            
            document.addEventListener('DOMContentLoaded', () => {{
                Chart.register(ChartDataLabels);
                document.getElementById('filterButton').addEventListener('click', updateDashboard);
                
                const wordCloudCtx = document.getElementById('wordCloudChart').getContext('2d');
                new Chart(wordCloudCtx, {{
                    type: 'wordCloud',
                    data: {{
                        labels: topWordsData.map(item => item[0]),
                        datasets: [{{
                            label: '',
                            data: topWordsData.map(item => item[1] / 2.5)
                        }}]
                    }},
                    options: {{
                        title: {{
                            display: true,
                            text: "Chart.js Word Cloud"
                        }},
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            datalabels: {{
                                display: false
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        const originalValue = topWordsData[context.dataIndex][1];
                                        return context.label + ': ' + originalValue;
                                    }}
                                }}
                            }}
                        }},
                        font: {{
                            weight: 'normal',
                            min: 5,
                            max: 20
                        }}
                    }}
                }});

                updateDashboard();
            }});
        </script>
    </body>
    </html>
    """
    with open('relatorio.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Relatório gerado: relatorio.html")

if __name__ == '__main__':
    generate_report()