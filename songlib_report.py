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

def get_song_title(song_data):
    # return f"{song_data['title']} - {song_data['author']}"
    return f"{song_data['title']}"

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

    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>IBM - Estatísticas do Louvor</title>
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
        <h1>Estatísticas do Ministério de Louvor</h1>

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
            <h2>Músicas Cadastradas Menos Cantadas</h2>
            <canvas id="leastUsedSongsChart"></canvas>
        </div>

        <div class="container">
            <h2>Autores/Intérpretes Mais Frequentes</h2>
            <canvas id="topAuthorsChart"></canvas>
        </div>


        <div class="container">
            <h2>Músicas Mais Escolhidas como Início do Período de Louvor</h2>
            <canvas id="firstSongsChart"></canvas>
        </div>

        <div class="container">
            <h2>Músicas Mais Escolhidas como Final do Período de Louvor</h2>
            <canvas id="lastSongsChart"></canvas>
        </div>
        
        <div class="container">
            <h2>Músicas Mais Escolhidas para Oferta</h2>
            <canvas id="offeringSongsChart"></canvas>
        </div>

        <div class="container">
            <h2>Músicas Mais Escolhidas para Pão</h2>
            <canvas id="breadSongsChart"></canvas>
        </div>

        <div class="container">
            <h2>Músicas Mais Escolhidas para Cálice</h2>
            <canvas id="wineSongsChart"></canvas>
        </div>

        <div class="container">
            <h2>Cultos por Dirigente</h2>
            <canvas id="singersChart"></canvas>
        </div>

        <div class="container-limited-height">
            <h2>Tonalidades Preferidas por Dirigente</h2>
            <canvas id="singerKeysChart"></canvas>
        </div>

        <div class="container">
            <h2>Top 10 Músicas por Dirigente</h2>
            <canvas id="singerTopSongsChart"></canvas>
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
        </script>
    </body>
    </html>
    """

    with open('songlib_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Relatório gerado: songlib_report.html")

if __name__ == '__main__':
    generate_report()