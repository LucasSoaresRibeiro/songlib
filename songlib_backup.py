from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os

REPROCESSAR_MUSICAS = False
REPROCESSAR_SETS = False

def init(site_url):

    # Configuração do Selenium WebDriver
    driver = webdriver.Chrome()  # Certifique-se de ter o chromedriver instalado e no PATH
    driver.get(site_url)
    time.sleep(2)

    # realiza login
    driver.find_element(By.ID, "id_email").send_keys("lucas.sax@gmail.com")
    driver.find_element(By.ID, "id_password").send_keys("123456")
    driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[1]/form/div[4]/button").click()
    time.sleep(2)

    return driver

def finish():
    driver.quit()

def salvar_backup_musicas(driver, site_url):

    # abre a biblioteca
    driver.get(site_url)
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="songbrowser"]/form/div/div[2]/div/button[2]').click()
    time.sleep(3)
    
    # lê todas as músicas da biblioteca
    songs_element = driver.find_elements(By.CSS_SELECTOR, 'a[data-songid]')

    songs = []
    for song_element in songs_element:
        songs.append({
            'songlib_url': song_element.get_attribute('href'),
            'id': song_element.get_attribute('data-songid'),
            'title': song_element.text,
        })

    songs = [song for song in songs if song['title'] != '']
    
    # salva músicas
    counter = 0
    for song in songs:

        counter += 1
        print('-'*20)
        print(f'Processando Musicas {counter}/{len(songs)} ...')

        file_name = f"songs\{song['id']}.json"

        if (os.path.isfile(file_name) and not REPROCESSAR_MUSICAS):
            continue

        try:

            driver.get(f"{song['songlib_url']}/edit")
            time.sleep(2)

            # salvar meta dados
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

            # salvar musica
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(song, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(e)

    # Update song_files.txt with the current list of songs
    song_files = [f"{song['id']}.json" for song in songs]
    song_files.sort()
    with open('web/data/song_files.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(song_files))

    print(f'Total de musicas cadastradas: {len(songs)}')
    print('song_files.txt atualizado com sucesso!')

def salvar_backup_sets(driver, site_url):

    # abre a biblioteca
    driver.get(site_url)
    time.sleep(3)
    
    # lê todas as músicas da biblioteca
    set_elements = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr td a[href]')

    data_sets = []
    for set_element in set_elements:
        data_sets.append({
            "id": set_element.get_attribute('href').split('/')[-2],
            "url": set_element.get_attribute('href'), 
        })
    
    # salva músicas
    counter = 0
    for data_set in data_sets:

        counter += 1
        print('-'*20)
        print(f'Processando Sets {counter}/{len(data_sets)} ...')
        
        file_name = f"sets\{data_set['id']}.json"

        if (os.path.isfile(file_name) and not REPROCESSAR_SETS):
            continue

        try:

            driver.get(data_set['url'])
            time.sleep(2)

            # salvar meta dados
            data_set['title'] = driver.find_element(By.ID, 'id_title').get_attribute('value')
            data_set['notes'] = driver.find_element(By.ID, 'id_notes').get_attribute('value')
            data_set['date'] = driver.find_element(By.ID, 'id_date').get_attribute('value')
            data_set['leader'] = driver.find_element(By.ID, 'id_leader').get_attribute('value')
            data_set['is_draft'] = driver.find_element(By.ID, 'id_draft').is_selected()
            
            data_set['songs'] = []

            song_elements_song_id = driver.find_elements(By.CSS_SELECTOR, 'input.songid')
            song_elements_href = driver.find_elements(By.CSS_SELECTOR, 'a')
            song_elements_no = driver.find_elements(By.CSS_SELECTOR, 'td.songno')
            song_elements_key = driver.find_elements(By.CSS_SELECTOR, 'select[name$="-key"] option[selected]')
            song_elements_use_b = driver.find_elements(By.CSS_SELECTOR, 'select[name$="-key_style"] option[selected]')

            music_counter = 0
            for song_element_song_id in song_elements_song_id:
                song = {}
                song['song_id'] = int(song_elements_song_id[music_counter].get_attribute('value'))
                song['no'] = song_elements_no[music_counter].text
                song['key'] = song_elements_key[music_counter].text
                song['use_b'] = song_elements_use_b[music_counter].text == 'Use ♭'
                song['notes'] = driver.find_element(By.ID, f'id_song-{music_counter}-notes').get_attribute('value')

                data_set['songs'].append(song)
                music_counter += 1

            # salvar musica
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(data_set, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(e)

    # Update song_files.txt with the current list of songs
    set_files = [f"{data_set['id']}.json" for data_set in data_sets]
    set_files.sort()
    with open('web/data/set_files.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(set(set_files)))

    print(f'Total de repertórios cadastrados: {len(data_sets)}')
    print('set_files.txt atualizado com sucesso!')

# Exemplo de uso
URL_SONGLIB_SONGS = 'https://songlib.com/songs/4297'
URL_SONGLIB_SETS = 'https://songlib.com/sets/4297'
driver = init(URL_SONGLIB_SONGS)
salvar_backup_sets(driver, URL_SONGLIB_SETS)
salvar_backup_musicas(driver, URL_SONGLIB_SONGS)
finish()