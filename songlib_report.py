import os
import json
from collections import Counter

SETS_DIR = 'c:\\Lucas\\Repos\\pessoal\\github\\songlib\\sets'
SONGS_DIR = 'c:\\Lucas\\Repos\\pessoal\\github\\songlib\\songs'

def generate_report():
    total_sets = 0
    total_songs = 0
    all_songs_in_sets = []
    singers = Counter()

    # Process set files
    for filename in os.listdir(SETS_DIR):
        if filename.endswith('.json'):
            total_sets += 1
            filepath = os.path.join(SETS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                set_data = json.load(f)
                total_songs += len(set_data.get('songs', []))
                for song in set_data.get('songs', []):
                    all_songs_in_sets.append(song['song_id'])
                
                title = set_data.get('title', '')
                if '-' in title:
                    singer = title.split('-')[-1].strip()
                    singers[singer] += 1

    # Sort singers by their event count in descending order
    sorted_singers = sorted(singers.items(), key=lambda item: item[1], reverse=True)
    singers_labels = [singer for singer, count in sorted_singers]
    singers_data = [count for singer, count in sorted_singers]

    song_occurrence_counts = Counter(all_songs_in_sets)
    top_songs = song_occurrence_counts.most_common(10) # Get top 10 songs

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
        <p>- Período analisado: {total_sets}</p>
        <p>- Músicas cantadas: {total_songs}</p>
        <p>- Músicas cadastradas: {total_sets}</p>
        <p>- Número de programações: {total_sets}</p>

        <h2>Eventos por Dirigente</h2>
        <canvas id="singersChart"></canvas>

        <h2>Ocorrências das Músicas Mais Frequentes</h2>
        <canvas id="topSongsChart"></canvas>

        <script>
            // Data for Singers Chart
            const singersData = {{
                labels: {json.dumps(singers_labels)},
                datasets: [{{
                    label: 'Número de Eventos',
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
                labels: {json.dumps([f"Song ID: {s_id}" for s_id, _ in top_songs])},
                datasets: [{{
                    label: 'Ocorrências',
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
        </script>
    </body>
    </html>
    """

    with open('songlib_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Relatório gerado: songlib_report.html")

if __name__ == '__main__':
    generate_report()