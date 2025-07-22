import os
import json
from collections import Counter
from datetime import datetime

SETS_DIR = 'c:\\Lucas\\Repos\\pessoal\\github\\songlib\\sets'
SONGS_DIR = 'c:\\Lucas\\Repos\\pessoal\\github\\songlib\\songs'
SINGERS = {
    "Geraldo": 0,
    "Eric": 0,
    "Amanda": 0,
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
    singers = Counter()

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
                total_songs_used += len(set_data.get('songs', []))
                for song in set_data.get('songs', []):

                    # Look up song title from songs directory
                    song_file = os.path.join(SONGS_DIR, f"{song['song_id']}.json")
                    if os.path.exists(song_file):
                        with open(song_file, 'r', encoding='utf-8') as sf:
                            song_data = json.load(sf)
                            all_songs_in_sets.append(song_data['title'])
                            if 'author' in song_data:
                                all_authors_in_sets.append(song_data['author'])
                
                title = set_data.get('title', '')
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

    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relatório SongLib</title>
        <link rel="stylesheet" href="formatacao/songlib.css">
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

        <h2>Resumo:</h2>
        {f'<p>- Período: De {min(set_dates).strftime("%d/%m/%Y")} até {max(set_dates).strftime("%d/%m/%Y")}</p>' if set_dates else ''}
        <p>- Músicas cadastradas: {total_songs}</p>
        <p>- Número de cultos/programações: {total_sets}</p>
        <p>- Média de músicas cantadas por programações: {int(round(total_songs_used/total_sets, 0))}</p>
        <p>- Total de músicas cantadas: {total_songs_used}</p>

        <h2>Cultos por Dirigente</h2>
        <canvas id="singersChart"></canvas>

        <h2>Músicas Mais Cantadas</h2>
        <canvas id="topSongsChart"></canvas>

        <h2>Autores/Intérpretes Mais Frequentes</h2>
        <canvas id="topAuthorsChart"></canvas>

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
        </script>
    </body>
    </html>
    """

    with open('songlib_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Relatório gerado: songlib_report.html")

if __name__ == '__main__':
    generate_report()