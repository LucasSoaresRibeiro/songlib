from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import json
import time
import os
import sys
import argparse

def init(site_url, username, password):
    driver = webdriver.Chrome()
    driver.get(site_url)
    time.sleep(2)

    # Login
    driver.find_element(By.ID, "id_email").send_keys(username)
    driver.find_element(By.ID, "id_password").send_keys(password)
    driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[1]/form/div[4]/button").click()
    time.sleep(2)

    return driver

def finish(driver):
    driver.quit()

def is_future_date(date_str):
    try:
        # Convert date string from DD/MM/YYYY to datetime object
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        return date_obj > datetime.now()
    except:
        return False

def salvar_backup_sets_futuros(driver, site_url):
    # Open library
    driver.get(site_url)
    time.sleep(3)
    
    # Read all sets from library
    set_elements = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr td a[href]')

    data_sets = []
    for set_element in set_elements:
        data_sets.append({
            "id": set_element.get_attribute('href').split('/')[-2],
            "url": set_element.get_attribute('href'), 
        })
    
    # Process sets
    counter = 0
    future_song_ids = set()
    
    for data_set in data_sets:
        try:
            driver.get(data_set['url'])
            time.sleep(2)

            # Get set date
            date = driver.find_element(By.ID, 'id_date').get_attribute('value')
            
            # Skip if not a future date
            if not is_future_date(date):
                # print(f'Processing Future Set finished.')
                break

            counter += 1
            print('-'*20)
            print(f'Processing Future Set {counter} ...')
            
            file_name = f"sets\{data_set['id']}.json"

            # Save set metadata
            data_set['title'] = driver.find_element(By.ID, 'id_title').get_attribute('value')
            data_set['notes'] = driver.find_element(By.ID, 'id_notes').get_attribute('value')
            data_set['date'] = date
            data_set['leader'] = driver.find_element(By.ID, 'id_leader').get_attribute('value')
            data_set['is_draft'] = driver.find_element(By.ID, 'id_draft').is_selected()
            
            data_set['songs'] = []

            # Get song elements
            song_elements_song_id = driver.find_elements(By.CSS_SELECTOR, 'input.songid')
            song_elements_no = driver.find_elements(By.CSS_SELECTOR, 'td.songno')
            song_elements_key = driver.find_elements(By.CSS_SELECTOR, 'select[name$="-key"] option[selected]')
            song_elements_use_b = driver.find_elements(By.CSS_SELECTOR, 'select[name$="-key_style"] option[selected]')

            music_counter = 0
            for song_element_song_id in song_elements_song_id:
                song = {}
                song_id = int(song_elements_song_id[music_counter].get_attribute('value'))
                song['song_id'] = song_id
                song['no'] = song_elements_no[music_counter].text
                song['key'] = song_elements_key[music_counter].text
                song['use_b'] = song_elements_use_b[music_counter].text == 'Use ♭'
                song['notes'] = driver.find_element(By.ID, f'id_song-{music_counter}-notes').get_attribute('value')

                data_set['songs'].append(song)
                future_song_ids.add(song_id)
                music_counter += 1

            # Save set
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(data_set, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error processing set {data_set['id']}: {e}")

    print(f'Total future sets processed: {counter}')
    return future_song_ids

def salvar_backup_musicas_selecionadas(driver, site_url, song_ids):
    if not song_ids:
        print("No songs to backup")
        return

    # Open library
    driver.get(site_url)
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="songbrowser"]/form/div/div[2]/div/button[2]').click()
    time.sleep(3)
    
    counter = 0
    for song_id in song_ids:
        counter += 1
        print('-'*20)
        print(f'Processing Song {counter}/{len(song_ids)} ...')

        file_name = f"songs\{song_id}.json"
        song_url = f"https://songlib.com/songs/4297/{song_id}"

        try:
            driver.get(f"{song_url}/edit")
            time.sleep(2)

            song = {
                'songlib_url': song_url,
                'id': str(song_id),
            }

            # Save metadata
            song['title'] = driver.find_element(By.ID, 'id_title').get_attribute('value')
            song['author'] = driver.find_element(By.ID, 'id_author').get_attribute('value')
            song['notes'] = driver.find_element(By.ID, 'id_notes').get_attribute('value')
            song['year'] = driver.find_element(By.ID, 'id_year').get_attribute('value')
            song['key'] = driver.find_element(By.ID, 'id_key').get_attribute('value')
            song['ccli'] = driver.find_element(By.ID, 'id_ccli').get_attribute('value')
            song['copyright'] = driver.find_element(By.ID, 'id_copyright').get_attribute('value')
            song['time_sig'] = driver.find_element(By.ID, 'id_time_sig').get_attribute('value')
            song['tempo'] = driver.find_element(By.ID, 'id_tempo').get_attribute('value')
            song['feel'] = driver.find_element(By.ID, 'id_feel').get_attribute('value')
            song['theme'] = driver.find_element(By.ID, 'id_theme').get_attribute('value')
            song['tags'] = driver.find_element(By.ID, 'id_tags').get_attribute('value')
            song['url'] = driver.find_element(By.ID, 'id_url').get_attribute('value')
            song['chord_chart'] = driver.find_element(By.ID, 'id_chord_chart').get_attribute('value')

            # Save song
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(song, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error processing song {song_id}: {e}")

    print(f'Total songs processed: {counter}')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Backup future sets and their songs from Songlib')
    parser.add_argument('--username', required=True, help='Songlib username')
    parser.add_argument('--password', required=True, help='Songlib password')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    
    URL_SONGLIB_SONGS = 'https://songlib.com/songs/4297'
    URL_SONGLIB_SETS = 'https://songlib.com/sets/4297'
    
    driver = init(URL_SONGLIB_SONGS, args.username, args.password)
    
    # First get all future sets and collect song IDs
    future_song_ids = salvar_backup_sets_futuros(driver, URL_SONGLIB_SETS)
    
    # Then backup only the songs that are used in future sets
    salvar_backup_musicas_selecionadas(driver, URL_SONGLIB_SONGS, future_song_ids)
    
    finish(driver)