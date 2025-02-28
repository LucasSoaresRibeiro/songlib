import os
import json
from pathlib import Path

def get_song_files(songs_dir):
    """Get all song files from the songs directory."""
    song_files = []
    for file in os.listdir(songs_dir):
        if file.endswith('.json'):
            song_files.append(os.path.join(songs_dir, file))
    return song_files

def load_song(file_path):
    """Load a song from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_title(title):
    """Normalize a song title by removing parentheses and extra spaces."""
    # Remove content in parentheses and extra spaces
    base_title = title.split('(')[0].strip()
    return base_title.lower()

def find_related_songs(songs_dir):
    """Find related songs based on title similarity."""
    song_files = get_song_files(songs_dir)
    relationships = []
    
    # Create a dictionary of normalized titles to file paths
    title_map = {}
    for file_path in song_files:
        song = load_song(file_path)
        norm_title = normalize_title(song['title'])
        
        if norm_title not in title_map:
            title_map[norm_title] = []
        title_map[norm_title].append(os.path.basename(file_path))
    
    # Create relationships for songs with matching normalized titles
    for title, files in title_map.items():
        if len(files) > 1:
            # Sort files to ensure consistent ordering
            files.sort()
            # Create relationships for each file
            relationships.append(','.join(files))
    
    return relationships

def save_relationships(relationships, output_file):
    """Save relationships to a text file, with each file and all its related files on a single line."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for related_files in relationships:
            # Write each file and all its related files on a single line
            f.write(related_files+'\n')

def main():
    # Get the songs directory path
    script_dir = Path(__file__).parent
    songs_dir = script_dir / 'songs'
    output_file = script_dir / 'web/song_relationships.txt'
    
    # Find and save relationships
    relationships = find_related_songs(str(songs_dir))
    save_relationships(relationships, output_file)
    print(f'Relationships saved to {output_file}')

if __name__ == '__main__':
    main()