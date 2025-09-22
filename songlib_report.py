import json
import os
from collections import Counter, defaultdict
import requests
from datetime import datetime, timedelta
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

# Open-Meteo Historical Weather API configuration
# WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
# DEFAULT_LATITUDE = -23.5505  # São Paulo latitude
# DEFAULT_LONGITUDE = -46.6333 # São Paulo longitude
WEATHER_API_URL = "https://archive-api.open-meteo.com/v1/era5"
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

def get_song_title(song_data):
    # return f"{song_data['title']} - {song_data['author']}"
    return f"{song_data['title']}"

def get_weather_data(date_str, latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date_str,
        "end_date": date_str,
        "hourly": "precipitation",
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        # Check if any hourly precipitation is greater than 0
        if "hourly" in data and "precipitation" in data["hourly"]:
            for precip in data["hourly"]["precipitation"]:
                if precip != None and precip > .15:
                    return True  # It rained
        return False  # It did not rain or no precipitation data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data for {date_str}: {e}")
        return False

def generate_report():
    total_sets = 0
    total_songs = 0
    total_songs_used = 0
    all_songs_in_sets = []
    all_authors_in_sets = []
    all_first_songs_in_sets = []
    all_last_songs_in_sets = []
    offering_songs = []
    bread_songs = []
    wine_songs = []
    singers = Counter()
    singer_song_keys = {singer: Counter() for singer in SINGERS.keys()}
    singer_top_songs = {singer: Counter() for singer in SINGERS.keys()}
    weather_by_singer = defaultdict(lambda: {'rain': 0, 'no_rain': 0})
    all_song_lyrics = []

    # Process song files
    for filename in os.listdir(SONGS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(SONGS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                song_data = json.load(f)
                if 'chord_chart' in song_data and song_data['chord_chart']:
                    all_song_lyrics.append(song_data['chord_chart'])
    total_songs = len(os.listdir(SONGS_DIR))

    # Generate word cloud data
    word_counts = Counter()
    stop_words = set(stopwords.words('portuguese'))
    # Add custom stop words if necessary
    custom_stop_words = {'pra','intro', 'refrão', 'fim', 'verso', 'ponte', 'pre', 'solo', 'final', 'bis', 'volta', 'parte', 'coda', 'tag', 'adlib', 'interludio', 'instrumental', 'outro', 'fade', 'in', 'out', 'repeat', 'x', '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x', '10x', 'etc', 'e', 'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'sem', 'sobre', 'sob', 'entre', 'até', 'após', 'ante', 'contra', 'desde', 'durante', 'mediante', 'perante', 'segundo', 'salvo', 'tirante', 'trás', 'através', 'afora', 'dentro', 'fora', 'perto', 'longe', 'abaixo', 'acima', 'adiante', 'atrás', 'defronte', 'depois', 'diante', 'embaixo', 'emcima', 'enfim', 'então', 'logo', 'mais', 'menos', 'muito', 'pouco', 'quase', 'sempre', 'tarde', 'cedo', 'nunca', 'jamais', 'agora', 'ainda', 'já', 'ontem', 'hoje', 'amanhã', 'aqui', 'ali', 'aí', 'cá', 'lá', 'além', 'aquém', 'onde', 'aonde', 'donde', 'para onde', 'como', 'assim', 'bem', 'mal', 'melhor', 'pior', 'devagar', 'depressa', 'grátis', 'junto', 'separado', 'só', 'somente', 'apenas', 'inclusive', 'exclusivamente', 'certamente', 'provavelmente', 'talvez', 'sim', 'não', 'claro', 'decerto', 'realmente', 'verdadeiramente', 'aparentemente', 'possivelmente', 'quissá', 'acaso', 'porventura', 'talvez', 'se', 'embora', 'conforme', 'como', 'enquanto', 'quando', 'apenas', 'mal', 'assim que', 'logo que', 'desde que', 'até que', 'para que', 'a fim de que', 'porque', 'pois', 'porquanto', 'como', 'já que', 'visto que', 'uma vez que', 'seja', 'ou', 'nem', 'mas', 'porém', 'contudo', 'todavia', 'entretanto', 'no entanto', 'portanto', 'logo', 'por conseguinte', 'consequentemente', 'assim', 'destarte', 'desse modo', 'dessa forma', 'à medida que', 'à proporção que', 'quanto mais', 'quanto menos', 'quanto maior', 'quanto menor', 'que', 'se', 'como', 'conforme', 'segundo', 'consoante', 'assim como', 'bem como', 'tanto quanto', 'mais que', 'menos que', 'tão quanto', 'tão como', 'tal qual', 'qual', 'que', 'cujo', 'cuja', 'cujos', 'cujas', 'onde', 'quando', 'como', 'quanto', 'por que', 'para que', 'se', 'caso', 'contanto que', 'desde que', 'a menos que', 'exceto se', 'salvo se', 'sem que', 'dado que', 'posto que', 'uma vez que', 'ainda que', 'embora', 'conquanto', 'posto que', 'se bem que', 'mesmo que', 'por mais que', 'por menos que', 'apesar de que', 'não obstante', 'conforme', 'como', 'segundo', 'consoante', 'assim como', 'bem como', 'tanto quanto', 'mais que', 'menos que', 'tão quanto', 'tão como', 'tal qual', 'qual', 'que', 'cujo', 'cuja', 'cujos', 'cujas', 'onde', 'quando', 'como', 'quanto', 'por que', 'para que', 'se', 'caso', 'contanto que', 'desde que', 'a menos que', 'exceto se', 'salvo se', 'sem que', 'dado que', 'posto que', 'uma vez que', 'ainda que', 'embora', 'conquanto', 'posto que', 'se bem que', 'mesmo que', 'por mais que', 'por menos que', 'apesar de que', 'não obstante'}
    stop_words.update(custom_stop_words)

    # temp
    stop_words = custom_stop_words

    for lyrics_block in all_song_lyrics:
        # Remove chord notations (lines starting with . or containing | or [ ] or ( ) or { } or numbers)
        cleaned_lyrics = []
        for line in lyrics_block.split('\n'):
            # Remove lines that look like chord lines or structural markers
            if not (line.strip().startswith('.') or
                    '|' in line or
                    '[' in line or
                    '(' in line or
                    '{' in line or
                    any(char.isdigit() for char in line)):
                cleaned_lyrics.append(line)
        text = ' '.join(cleaned_lyrics)

        # Remove punctuation and convert to lowercase
        text = re.sub(r'[\W_]+', ' ', text).lower()
        words = text.split()
        
        # Filter out stop words and single-character words
        filtered_words = [word.upper() for word in words if word not in stop_words and len(word) > 1]
        word_counts.update(filtered_words)

    # Get the top N words for the word cloud
    top_words = word_counts.most_common(100)

    # Process set files
    set_dates = []
    for filename in os.listdir(SETS_DIR):
        if filename.endswith('.json'):
            total_sets += 1
            filepath = os.path.join(SETS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                set_data = json.load(f)
                title = set_data.get('title', '')
                total_songs_used += len(set_data.get('songs', []))
                songs_in_set = set_data.get('songs', [])
                if songs_in_set:
                    first_song_id = songs_in_set[0]['song_id']
                    last_song_id = songs_in_set[-1]['song_id']
                    # Store first and last song IDs for later processing
                    all_first_songs_in_sets.append(first_song_id)
                    all_last_songs_in_sets.append(last_song_id)

                for song in songs_in_set:

                    # Look up song title from songs directory
                    song_file = os.path.join(SONGS_DIR, f"{song['song_id']}.json")
                    if os.path.exists(song_file):
                        with open(song_file, 'r', encoding='utf-8') as sf:
                            song_data = json.load(sf)
                            all_songs_in_sets.append(get_song_title(song_data))
                            if 'author' in song_data and song_data['author'] != '':
                                all_authors_in_sets.append(song_data['author'])
                            if 'key' in song_data and song_data['key'] != '':
                                current_singer = next((s for s in SINGERS.keys() if s in title or s in title.upper()), None)
                                if current_singer:
                                    key = song['key'].split(" ")[0]
                                    if key in ['A#', 'Bb']:
                                        key = 'A# / Bb'
                                    if key in ['G#', 'Ab']:
                                        key = 'G# / Ab'
                                    if key in ['C#', 'Db']:
                                        key = 'C# / Db'
                                    if key in ['F#', 'Gb']:
                                        key = 'F# / Gb'
                                    singer_song_keys[current_singer][key] += 1
                                if current_singer:
                                    singer_top_songs[current_singer][get_song_title(song_data)] += 1
                            if 'notes' in song and 'Oferta' in song['notes']:
                                offering_songs.append(get_song_title(song_data))
                            if 'notes' in song and 'Pão' in song['notes']:
                                bread_songs.append(get_song_title(song_data))
                            if 'notes' in song and 'Cálice' in song['notes']:
                                wine_songs.append(get_song_title(song_data))
                for singer in SINGERS.keys():
                    if singer in title or singer in title.upper():
                        SINGERS[singer] += 1
                
                if 'date' in set_data:
                    set_date_str = set_data['date']
                    set_dates.append(datetime.strptime(set_date_str, "%d/%m/%Y"))
                    
                    current_singer = next((s for s in SINGERS.keys() if s in title or s in title.upper()), None)
                    if current_singer:
                        # Fetch weather data for the set date
                        it_rained = get_weather_data(datetime.strptime(set_date_str, "%d/%m/%Y").strftime("%Y-%m-%d"), DEFAULT_LATITUDE, DEFAULT_LONGITUDE)
                        if it_rained:
                            weather_by_singer[current_singer]['rain'] += 1
                        else:
                            weather_by_singer[current_singer]['no_rain'] += 1

    # Sort singers by their event count in descending order
    sorted_singers = sorted(SINGERS.items(), key=lambda item: item[1], reverse=True)
    singers_labels = [singer for singer, count in sorted_singers]
    singers_data = [count for singer, count in sorted_singers]

    song_occurrence_counts = Counter(all_songs_in_sets)

    top_songs_with_titles = []
    for song_title, count in song_occurrence_counts.most_common(10):
        top_songs_with_titles.append((song_title, count))

    top_songs = top_songs_with_titles # Get top 10 songs

    author_occurrence_counts = Counter(all_authors_in_sets)
    top_authors_with_titles = []
    for author_name, count in author_occurrence_counts.most_common(10):
        top_authors_with_titles.append((author_name, count))

    top_authors = top_authors_with_titles # Get top 10 authors

    # Process first songs
    first_song_titles = []
    for song_id in all_first_songs_in_sets:
        song_file = os.path.join(SONGS_DIR, f"{song_id}.json")
        if os.path.exists(song_file):
            with open(song_file, 'r', encoding='utf-8') as sf:
                song_data = json.load(sf)
                first_song_titles.append(get_song_title(song_data))
    first_song_occurrence_counts = Counter(first_song_titles)
    top_first_songs = first_song_occurrence_counts.most_common(10)

    # Process last songs
    last_song_titles = []
    for song_id in all_last_songs_in_sets:
        song_file = os.path.join(SONGS_DIR, f"{song_id}.json")
        if os.path.exists(song_file):
            with open(song_file, 'r', encoding='utf-8') as sf:
                song_data = json.load(sf)
                last_song_titles.append(get_song_title(song_data))
    last_song_occurrence_counts = Counter(last_song_titles)
    top_last_songs = last_song_occurrence_counts.most_common(10)

    # Process least used songs
    all_song_titles = []
    for filename in os.listdir(SONGS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(SONGS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                song_data = json.load(f)
                all_song_titles.append(get_song_title(song_data))

    least_used_songs_counts = Counter(all_song_titles)
    # Subtract songs that have been used in sets
    for song_title in all_songs_in_sets:
        if song_title in least_used_songs_counts:
            least_used_songs_counts[song_title] -= 1

    # Filter out songs that have been used at least once (count > 0 after subtraction)
    # And then get the 10 least used songs (those with the lowest counts, including 0)
    least_used_songs = sorted([item for item in least_used_songs_counts.items() if item[1] >= 0], key=lambda item: item[1])[:10]

    # Prepare data for Singer Keys Chart
    all_unique_keys = set()

    # Prepare data for Singer Top Songs Chart
    singer_top_songs_chart_data = {}
    for singer_name, song_counts in singer_top_songs.items():
        singer_top_songs_chart_data[singer_name] = song_counts.most_common(10)

    for singer_name, key_counts in singer_song_keys.items():
        for key, _ in key_counts.most_common(1000):
        # for key, _ in key_counts:
            all_unique_keys.add(key)

    sorted_unique_keys = sorted(list(all_unique_keys))

    singer_keys_chart_datasets = []
    for singer_name in SINGERS.keys():
        data = []
        for key in sorted_unique_keys:
            data.append(singer_song_keys[singer_name].get(key, 0))
        singer_keys_chart_datasets.append({
            'label': singer_name,
            'data': data,
            'backgroundColor': f'rgba({hash(singer_name) % 256}, {hash(singer_name + "a") % 256}, {hash(singer_name + "b") % 256}, 0.6)',
            'borderColor': f'rgba({hash(singer_name) % 256}, {hash(singer_name + "a") % 256}, {hash(singer_name + "b") % 256}, 1)',
            'borderWidth': 1
        })

    report_data = {
        'total_sets': total_sets,
        'total_songs': total_songs,
        'total_songs_used': total_songs_used,
        'top_songs': top_songs,
        'top_authors': top_authors,
        'top_first_songs': top_first_songs,
        'top_last_songs': top_last_songs,
        'offering_songs': offering_songs,
        'bread_songs': bread_songs,
        'wine_songs': wine_songs,
        'singer_song_keys': singer_song_keys,
        'singer_top_songs': singer_top_songs,
        'weather_by_singer': weather_by_singer,
        'top_words': top_words
    }

    # Generate HTML report
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
    </head>
    <body>
        <div class="logo-container">
            <img src="images/logo.png" alt="Maranata Logo" class="logo" />
        </div>
        <h1>Estatísticas do Ministério de Louvor</h1>

        <div class="container">
            <h2>Resumo:</h2>
            <div class="dashboard-container">
                <div class="dashboard-block">
                    <div class="dashboard-block-title">Período Analisado</div>
                    <div class="dashboard-block-value">{min(set_dates).strftime("%d/%m/%Y")} a {max(set_dates).strftime("%d/%m/%Y")}</div>
                </div>
                <div class="dashboard-block">
                    <div class="dashboard-block-title">Músicas Cadastradas</div>
                    <div class="dashboard-block-value">{total_songs}</div>
                </div>
                <div class="dashboard-block">
                    <div class="dashboard-block-title">Cultos e Programações</div>
                    <div class="dashboard-block-value">{total_sets}</div>
                </div>
                <div class="dashboard-block">
                    <div class="dashboard-block-title">Média de Músicas por Programação</div>
                    <div class="dashboard-block-value">{int(round(total_songs_used/total_sets, 0))}</div>
                </div>
                <div class="dashboard-block">
                    <div class="dashboard-block-title">Total de Execuções de Música</div>
                    <div class="dashboard-block-value">{total_songs_used}</div>
                </div>
            </div>
        </div>

        <div class="container">
            <h2>Músicas Mais Cantadas 🔝</h2>
            <canvas id="topSongsChart"></canvas>
        </div>

        <div class="container" style="display: none;">
            <h2>Músicas Cadastradas Menos Cantadas</h2>
            <canvas id="leastUsedSongsChart"></canvas>
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
            <canvas id="singerTopSongsChart"></canvas>
        </div>

        <div class="chart-container">
            <h2>Índice de Precipitação por Dirigente ⛈️</h2>
            <canvas id="weatherBySingerChart"></canvas>
        </div>

        <div class="container-word-cloud">
            <h2>Palavras Mais Frequentes nas Músicas 🙏</h2>
            <canvas id="wordCloudChart" style="height: 400px;"></canvas>
        </div>

        <script>
            // Data for Singers Chart
            const singersData = {{
                labels: {json.dumps(singers_labels)},
                datasets: [{{
                    label: 'Quantidade',
                    data: {json.dumps(singers_data)},
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }}]
            }};

            const singersCtx = document.getElementById('singersChart').getContext('2d');
            new Chart(singersCtx, {{
                type: 'bar',
                data: singersData,
                options: {{
                    responsive: true,
                    indexAxis: 'y',
                    plugins: {{
                        datalabels: {{
                            anchor: 'end',
                            align: 'start',
                            formatter: (value, context) => {{
                                return value;
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});



            // Data for Top Songs Chart
            const topSongsData = {{
                labels: {json.dumps([f"{title}" for title, count in top_songs])},
                datasets: [{{
                    label: 'Quantidade',
                    data: {json.dumps([count for _, count in top_songs])},
                    backgroundColor: 'rgba(153, 102, 255, 0.6)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }}]
            }};

            const topSongsCtx = document.getElementById('topSongsChart').getContext('2d');
            new Chart(topSongsCtx, {{
                type: 'bar',
                data: topSongsData,
                options: {{
                    responsive: true,
                    indexAxis: 'y',
                    plugins: {{
                        datalabels: {{
                            anchor: 'end',
                            align: 'start',
                            formatter: (value, context) => {{
                                return value;
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});

            // Data for Top First Songs Chart
            const firstSongsData = {{
                labels: {json.dumps([f"{title}" for title, count in top_first_songs])},
                datasets: [{{
                    label: 'Quantidade',
                    data: {json.dumps([count for _, count in top_first_songs])},
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }}]
            }};

            const firstSongsCtx = document.getElementById('firstSongsChart').getContext('2d');
            new Chart(firstSongsCtx, {{
                type: 'bar',
                data: firstSongsData,
                options: {{
                    responsive: true,
                    indexAxis: 'y',
                    plugins: {{
                        datalabels: {{
                            anchor: 'end',
                            align: 'start',
                            formatter: (value, context) => {{
                                return value;
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});

            // Data for Top Last Songs Chart
            const lastSongsData = {{
                labels: {json.dumps([f"{title}" for title, count in top_last_songs])},
                datasets: [{{
                    label: 'Quantidade',
                    data: {json.dumps([count for _, count in top_last_songs])},
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }};

            const lastSongsCtx = document.getElementById('lastSongsChart').getContext('2d');
            new Chart(lastSongsCtx, {{
                type: 'bar',
                data: lastSongsData,
                options: {{
                    responsive: true,
                    indexAxis: 'y',
                    plugins: {{
                        datalabels: {{
                            anchor: 'end',
                            align: 'start',
                            formatter: (value, context) => {{
                                return value;
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});

            // Data for Top Authors Chart
            const topAuthorsData = {{
                labels: {json.dumps([f"{author}" for author, count in top_authors])},
                datasets: [{{
                    label: 'Quantidade',
                    data: {json.dumps([count for _, count in top_authors])},
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }}]
            }};

            const topAuthorsCtx = document.getElementById('topAuthorsChart').getContext('2d');
            new Chart(topAuthorsCtx, {{
                type: 'bar',
                data: topAuthorsData,
                options: {{
                    responsive: true,
                    indexAxis: 'y',
                    plugins: {{
                        datalabels: {{
                            anchor: 'end',
                            align: 'start',
                            formatter: (value, context) => {{
                                return value;
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});

            // Data for Singer Keys Chart
            const singerKeysData = {{
                labels: {json.dumps(sorted_unique_keys)},
                datasets: {json.dumps(singer_keys_chart_datasets)}
            }};

            const singerKeysCtx = document.getElementById('singerKeysChart').getContext('2d');
            new Chart(singerKeysCtx, {{
                type: 'radar',
                data: singerKeysData,
                options: {{
                    responsive: true,
                    indexAxis: 'y',
                    plugins: {{
                        datalabels: {{
                            anchor: 'end',
                            align: 'start',
                            formatter: (value, context) => {{
                                return value;
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
            
            // Data for Offering Songs Chart
            const offeringSongsData = {json.dumps({
                "labels": [item[0] for item in Counter(offering_songs).most_common(10)],
                "datasets": [{
                    "label": 'Quantidade',
                    "data": [item[1] for item in Counter(offering_songs).most_common(10)],
                    "backgroundColor": 'rgba(255, 159, 64, 0.6)',
                    "borderColor": 'rgba(255, 159, 64, 1)',
                    "borderWidth": 1
                }]
            })};

            const offeringSongsCtx = document.getElementById('offeringSongsChart').getContext('2d');
            new Chart(offeringSongsCtx, {{
                type: 'bar',
                data: offeringSongsData,
                options: {json.dumps({
                    "responsive": True,
                    "indexAxis": 'y',
                    "plugins": {
                        "datalabels": {
                            "anchor": 'end',
                            "align": 'start',
                            "formatter": "(value, context) => { return value; }"
                        }
                    },
                    "scales": {
                        "x": {
                            "beginAtZero": True
                        }
                    }
                })}
            }});

            // Data for Bread Songs Chart
            const breadSongsData = {json.dumps({
                "labels": [item[0] for item in Counter(bread_songs).most_common(10)],
                "datasets": [{
                    "label": 'Quantidade',
                    "data": [item[1] for item in Counter(bread_songs).most_common(10)],
                    "backgroundColor": 'rgba(75, 192, 192, 0.6)',
                    "borderColor": 'rgba(75, 192, 192, 1)',
                    "borderWidth": 1
                }]
            })};

            const breadSongsCtx = document.getElementById('breadSongsChart').getContext('2d');
            new Chart(breadSongsCtx, {{
                type: 'bar',
                data: breadSongsData,
                options: {json.dumps({
                    "responsive": True,
                    "indexAxis": 'y',
                    "plugins": {
                        "datalabels": {
                            "anchor": 'end',
                            "align": 'start',
                            "formatter": "(value, context) => { return value; }"
                        }
                    },
                    "scales": {
                        "x": {
                            "beginAtZero": True
                        }
                    }
                })}
            }});

            // Data for Wine Songs Chart
            const wineSongsData = {json.dumps({
                "labels": [item[0] for item in Counter(wine_songs).most_common(10)],
                "datasets": [{
                    "label": 'Quantidade',
                    "data": [item[1] for item in Counter(wine_songs).most_common(10)],
                    "backgroundColor": 'rgba(153, 102, 255, 0.6)',
                    "borderColor": 'rgba(153, 102, 255, 1)',
                    "borderWidth": 1
                }]
            })};

            const wineSongsCtx = document.getElementById('wineSongsChart').getContext('2d');
            new Chart(wineSongsCtx, {{
                type: 'bar',
                data: wineSongsData,
                options: {json.dumps({
                    "responsive": True,
                    "indexAxis": 'y',
                    "plugins": {
                        "datalabels": {
                            "anchor": 'end',
                            "align": 'start',
                            "formatter": "(value, context) => { return value; }"
                        }
                    },
                    "scales": {
                        "x": {
                            "beginAtZero": True
                        }
                    }
                })}
            }});

            // Data for Least Used Songs Chart
            const leastUsedSongsData = {json.dumps({
                "labels": [item[0] for item in least_used_songs],
                "datasets": [{
                    "label": 'Quantidade',
                    "data": [item[1] for item in least_used_songs],
                    "backgroundColor": 'rgba(255, 206, 86, 0.6)',
                    "borderColor": 'rgba(255, 206, 86, 1)',
                    "borderWidth": 1
                }]
            })};

            const leastUsedSongsCtx = document.getElementById('leastUsedSongsChart').getContext('2d');
            new Chart(leastUsedSongsCtx, {{
                type: 'bar',
                data: leastUsedSongsData,
                options: {json.dumps({
                    "responsive": True,
                    "indexAxis": 'y',
                    "plugins": {
                        "datalabels": {
                            "anchor": 'end',
                            "align": 'start',
                            "formatter": "(value, context) => { return value; }"
                        }
                    },
                    "scales": {
                        "x": {
                            "beginAtZero": True
                        }
                    }
                })}
            }});

            // Data for Singer Top Songs Chart
            const singerTopSongsData = {json.dumps(singer_top_songs_chart_data)};
            const singerTopSongsContainer = document.getElementById('singerTopSongsChart');
            
            for (const singerName in singerTopSongsData) {{
                const songs = singerTopSongsData[singerName];
                if (songs.length > 0) {{
                    const chartDiv = document.createElement('div');
                    chartDiv.className = 'singer-top-songs-chart';
                    chartDiv.innerHTML = `<h3>${{singerName}}</h3><canvas id="singerTopSongsChart_${{singerName}}"></canvas>`;
                    singerTopSongsContainer.parentNode.insertBefore(chartDiv, singerTopSongsContainer);

                    const ctx = document.getElementById(`singerTopSongsChart_${{singerName}}`).getContext('2d');
                    new Chart(ctx, {{
                        type: 'bar',
                        data: {{
                            labels: songs.map(item => item[0]),
                            datasets: [{{
                                label: 'Quantidade',
                                data: songs.map(item => item[1]),
                                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                                borderColor: 'rgba(75, 192, 192, 1)',
                                borderWidth: 1
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            indexAxis: 'y',
                            plugins: {{
                                datalabels: {{
                                    anchor: 'end',
                                    align: 'start',
                                    formatter: (value, context) => {{
                                        return value;
                                    }}
                                }}
                            }},
                            scales: {{
                                x: {{
                                    beginAtZero: true
                                }}
                            }}
                        }}
                    }});
                }}
            }}
            singerTopSongsContainer.remove();
            // Data for Weather by Singer Chart
            const weatherBySingerData = {json.dumps(weather_by_singer)};

            // Data for Word Cloud Chart
            const wordCloudData = {json.dumps(top_words)};
            const wordCloudCtx = document.getElementById('wordCloudChart').getContext('2d');
            new Chart(wordCloudCtx, {{
                type: 'wordCloud',
                data: {{
                    labels: wordCloudData.map(item => item[0]),
                    datasets: [{{
                        label: '',
                        data: wordCloudData.map(item => item[1]/2.5)
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
                        }}
                    }},
                    font: {{
                        weight: 'normal',
                        min: 5,
                        max: 20
                    }}
                }}
            }});

            const weatherLabels = Object.keys(weatherBySingerData);
            const rainData = weatherLabels.map(singer => weatherBySingerData[singer]['rain']);
            const noRainData = weatherLabels.map(singer => weatherBySingerData[singer]['no_rain']);

            const weatherCtx = document.getElementById('weatherBySingerChart').getContext('2d');
            new Chart(weatherCtx, {{
                type: 'bar',
                data: {{
                    labels: weatherLabels,
                    datasets: [
                        {{
                            label: 'Choveu',
                            data: rainData,
                            backgroundColor: 'rgba(75, 192, 192, 0.6)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }},
                        {{
                            label: 'Não Choveu',
                            data: noRainData,
                            backgroundColor: 'rgba(255, 99, 132, 0.6)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        x: {{
                            stacked: true,
                        }},
                        y: {{
                            stacked: true,
                            beginAtZero: true
                        }}
                    }},
                    plugins: {{
                        datalabels: {{
                            formatter: (value, context) => {{
                                return value > 0 ? value : '';
                            }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """

    with open('songlib_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Relatório gerado: songlib_report.html")

if __name__ == '__main__':
    generate_report()