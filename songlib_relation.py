import os
import json
import re
from pathlib import Path
from difflib import SequenceMatcher

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

def calculate_similarity_score(song1, song2):
    """Calculate a similarity score between two songs based on multiple factors."""
    score = 0
    
    # Check if titles are similar (ignoring case and parentheses)
    title1 = normalize_title(song1['title'])
    title2 = normalize_title(song2['title'])
    if title1 == title2:
        score += 5
    elif SequenceMatcher(None, title1, title2).ratio() > 0.8:
        score += 3
    
    # Check if they have the same key
    if song1['key'] == song2['key'] and song1['key'] != "":
        score += 2
    
    # Check if they have the same URL
    if song1['url'] == song2['url'] and song1['url'] != "":
        score += 4
    
    # Check for chord chart similarity
    if song1['chord_chart'] and song2['chord_chart']:
        # Extract just the chord patterns (lines starting with dots)
        chords1 = re.findall(r'\.[^\n]*', song1['chord_chart'])
        chords2 = re.findall(r'\.[^\n]*', song2['chord_chart'])
        
        # If both have chord patterns, compare them
        if chords1 and chords2:
            chord_similarity = SequenceMatcher(None, ''.join(chords1), ''.join(chords2)).ratio()
            if chord_similarity > 0.7:
                score += 3
        
        # Check for lyric similarity (non-chord lines)
        lyrics1 = [line.strip() for line in song1['chord_chart'].split('\n') 
                  if line.strip() and not line.strip().startswith('.')]
        lyrics2 = [line.strip() for line in song2['chord_chart'].split('\n') 
                  if line.strip() and not line.strip().startswith('.')]
        
        if lyrics1 and lyrics2:
            # Compare first few lines of lyrics if available
            sample_size = min(5, len(lyrics1), len(lyrics2))
            lyric_sample1 = ' '.join(lyrics1[:sample_size])
            lyric_sample2 = ' '.join(lyrics2[:sample_size])
            lyric_similarity = SequenceMatcher(None, lyric_sample1, lyric_sample2).ratio()
            if lyric_similarity > 0.7:
                score += 4
    
    return score

def find_related_songs(songs_dir):
    """Find related songs based on multiple similarity factors."""
    song_files = get_song_files(songs_dir)
    relationships = []
    song_data = {}
    
    # Load all songs first
    for file_path in song_files:
        song = load_song(file_path)
        song_data[os.path.basename(file_path)] = song
    
    # Create a dictionary to track relationships
    related_groups = {}
    processed_pairs = set()
    
    # Compare each song with every other song
    song_files_basenames = [os.path.basename(f) for f in song_files]
    for i, file1 in enumerate(song_files_basenames):
        for file2 in song_files_basenames[i+1:]:
            # Skip if we've already processed this pair
            pair_key = tuple(sorted([file1, file2]))
            if pair_key in processed_pairs:
                continue
            
            processed_pairs.add(pair_key)
            
            # Calculate similarity score
            similarity = calculate_similarity_score(song_data[file1], song_data[file2])
            
            # If similarity is above threshold, consider them related
            if similarity >= 6:  # Threshold can be adjusted
                # Add to related groups
                group_found = False
                
                # Check if either file is already in a group
                for group_id, files in related_groups.items():
                    if file1 in files or file2 in files:
                        related_groups[group_id].update([file1, file2])
                        group_found = True
                        break
                
                # If not found in any existing group, create a new group
                if not group_found:
                    group_id = len(related_groups)
                    related_groups[group_id] = {file1, file2}
    
    # Convert related groups to the required format
    for group_files in related_groups.values():
        if len(group_files) > 1:
            # Sort files to ensure consistent ordering
            sorted_files = sorted(group_files)
            relationships.append(','.join(sorted_files))
    
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