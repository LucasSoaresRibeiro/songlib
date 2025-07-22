import os
import json
from collections import Counter
from datetime import datetime

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

def generate_report():
    total_sets = 0
    total_songs = 0
    total_songs_used = 0
    all_songs_in_sets = []
    all_authors_in_sets = []
    all_first_songs_in_sets = []
    all_last_songs_in_sets = []
    singers = Counter()
    singer_song_keys = {singer: Counter() for singer in SINGERS.keys()}

    # Process song files
    total_songs = len(os.listdir(SONGS_DIR))

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
                            all_songs_in_sets.append(song_data['title'])
                            if 'author' in song_data and song_data['author'] != '':
                                all_authors_in_sets.append(song_data['author'])
                            if 'key' in song_data and song_data['key'] != '':
                                current_singer = next((s for s in SINGERS.keys() if s in title or s in title.upper()), None)
                                if current_singer:
                                    singer_song_keys[current_singer][song_data['key']] += 1
                for singer in SINGERS.keys():
                    if singer in title or singer in title.upper():
                        SINGERS[singer] += 1
                
                if 'date' in set_data:
                    set_dates.append(datetime.strptime(set_data['date'], "%d/%m/%Y"))

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
                first_song_titles.append(song_data['title'])
    first_song_occurrence_counts = Counter(first_song_titles)
    top_first_songs = first_song_occurrence_counts.most_common(10)

    # Process last songs
    last_song_titles = []
    for song_id in all_last_songs_in_sets:
        song_file = os.path.join(SONGS_DIR, f"{song_id}.json")
        if os.path.exists(song_file):
            with open(song_file, 'r', encoding='utf-8') as sf:
                song_data = json.load(sf)
                last_song_titles.append(song_data['title'])
    last_song_occurrence_counts = Counter(last_song_titles)
    top_last_songs = last_song_occurrence_counts.most_common(10)

    # Prepare data for Singer Keys Chart
    all_unique_keys = set()
    for singer_name, key_counts in singer_song_keys.items():
        for key, _ in key_counts.most_common(5):
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

    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relatório SongLib</title>
        <link rel="stylesheet" href="web/style/styles-report.css">
        <link href="https://fonts.googleapis.com/css2?family=Martian+Mono:wdth,wght@87.5,100..800&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,100..700;1,100..700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
    </head>
    <body>
        <div class="logo-container">
            <img src="images/logo.png" alt="Maranata Logo" class="logo" />
        </div>
        <h1>Relatório Ministério de Louvor</h1>

        <div class="container">
            <h2>Resumo:</h2>
            {f'<p>- Período: De {min(set_dates).strftime("%d/%m/%Y")} até {max(set_dates).strftime("%d/%m/%Y")}</p>' if set_dates else ''}
            <p>- Músicas cadastradas: {total_songs}</p>
            <p>- Número de cultos/programações: {total_sets}</p>
            <p>- Média de músicas cantadas por programação: {int(round(total_songs_used/total_sets, 0))}</p>
            <p>- Total de execuções de música: {total_songs_used}</p>
        </div>

        <div class="container">
            <h2>Músicas Mais Cantadas</h2>
            <canvas id="topSongsChart"></canvas>
        </div>

        <div class="container">
            <h2>Autores/Intérpretes Mais Frequentes</h2>
            <canvas id="topAuthorsChart"></canvas>
        </div>

        <div class="container">
            <h2>Cultos por Dirigente</h2>
            <canvas id="singersChart"></canvas>
        </div>

        <div class="container">
            <h2>Tonalidades Preferidas por Dirigente</h2>
            <canvas id="singerKeysChart"></canvas>
        </div>

        <div class="container">
            <h2>Músicas Mais Escolhidas como Início de Culto</h2>
            <canvas id="firstSongsChart"></canvas>
        </div>

        <div class="container">
            <h2>Músicas Mais Escolhidas como Final de Culto</h2>
            <canvas id="lastSongsChart"></canvas>
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
                type: 'bar',
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
        </script>
    </body>
    </html>
    """

    with open('songlib_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Relatório gerado: songlib_report.html")

if __name__ == '__main__':
    generate_report()