from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os

REPROCESSAR_MUSICAS = False

def salvar_backup(site_url):

    # Configuração do Selenium WebDriver
    driver = webdriver.Chrome()  # Certifique-se de ter o chromedriver instalado e no PATH
    driver.get(site_url)
    time.sleep(2)

    # realiza login
    driver.find_element(By.ID, "id_email").send_keys("lucas.sax@gmail.com")
    driver.find_element(By.ID, "id_password").send_keys("123456")
    driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[1]/form/div[4]/button").click()
    time.sleep(2)

    # abre a biblioteca
    driver.get(site_url)
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

    songs = [song for song in songs if song['title'] is not '']
    
    # salva músicas
    counter = 0
    for song in songs:

        counter += 1
        print('-'*20)
        print(f'Processando {counter}/{len(songs)} ...')

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

    driver.quit()

    print(f'Total de musicas cadastradas: {len(songs)}')

# Exemplo de uso
URL_DO_SONGLIB = 'https://songlib.com/songs/4297/'
salvar_backup(URL_DO_SONGLIB)