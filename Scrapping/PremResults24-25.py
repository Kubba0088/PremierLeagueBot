import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time


def initialize_db():
    conn = sqlite3.connect('prem_matches_stats_24_25.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS matches (
                 match_id TEXT PRIMARY KEY, 
                 home_team TEXT, 
                 away_team TEXT, 
                 goals_home_team INTEGER, 
                 goals_away_team INTEGER,
                 posiadanie_pilki_home_team REAL,
                 posiadanie_pilki_away_team REAL,
                 sytuacje_bramkowe_home_team INTEGER,
                 sytuacje_bramkowe_away_team INTEGER,
                 strzaly_na_bramke_home_team INTEGER,
                 strzaly_na_bramke_away_team INTEGER,
                 strzaly_niecelne_home_team INTEGER,
                 strzaly_niecelne_away_team INTEGER,
                 rzuty_rożne_home_team INTEGER,
                 rzuty_rożne_away_team INTEGER,
                 spalone_home_team INTEGER,
                 spalone_away_team INTEGER,
                 faule_home_team INTEGER,
                 faule_away_team INTEGER
                 )''')

    conn.commit()
    return conn, c


def match_exists(c, match_id):
    c.execute("SELECT match_id FROM matches WHERE match_id = ?", (match_id,))
    return c.fetchone() is not None


def add_match_to_db(c, match_id, home_team, away_team, goals_home_team, goals_away_team, stats):
    c.execute('''INSERT OR IGNORE INTO matches (match_id, home_team, away_team, goals_home_team, goals_away_team, 
                                                posiadanie_pilki_home_team, posiadanie_pilki_away_team, 
                                                sytuacje_bramkowe_home_team, sytuacje_bramkowe_away_team, 
                                                strzaly_na_bramke_home_team, strzaly_na_bramke_away_team, 
                                                strzaly_niecelne_home_team, strzaly_niecelne_away_team, 
                                                rzuty_rożne_home_team, rzuty_rożne_away_team, 
                                                spalone_home_team, spalone_away_team, 
                                                faule_home_team, faule_away_team)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (match_id, home_team, away_team, goals_home_team, goals_away_team,
               stats.get('Posiadanie piłki', (0.0, 0.0))[0], stats.get('Posiadanie piłki', (0.0, 0.0))[1],
               stats.get('Sytuacje bramkowe', (0, 0))[0], stats.get('Sytuacje bramkowe', (0, 0))[1],
               stats.get('Strzały na bramkę', (0, 0))[0], stats.get('Strzały na bramkę', (0, 0))[1],
               stats.get('Strzały niecelne', (0, 0))[0], stats.get('Strzały niecelne', (0, 0))[1],
               stats.get('Rzuty rożne', (0, 0))[0], stats.get('Rzuty rożne', (0, 0))[1],
               stats.get('Spalone', (0, 0))[0], stats.get('Spalone', (0, 0))[1],
               stats.get('Faule', (0, 0))[0], stats.get('Faule', (0, 0))[1]))


conn, c = initialize_db()

driver_path = 'C:/webdriver/chromedriver-win64/chromedriver.exe'
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://www.flashscore.pl/pilka-nozna/anglia/premier-league/wyniki/"
driver.get(url)

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

matches = soup.find_all('div', class_='event__match')

desired_stats = [
    "Posiadanie piłki",
    "Sytuacje bramkowe",
    "Strzały na bramkę",
    "Strzały niecelne",
    "Rzuty rożne",
    "Spalone",
    "Faule"
]

for match in matches:
    home_team = match.find('div', class_='event__homeParticipant').get_text(strip=True)
    away_team = match.find('div', class_='event__awayParticipant').get_text(strip=True)

    goals_home_team = int(match.find('div', class_='event__score--home').get_text(strip=True))
    goals_away_team = int(match.find('div', class_='event__score--away').get_text(strip=True))

    match_link = match.find('a', class_='eventRowLink')['href']
    match_id = match_link.split('/')[4]

    if match_exists(c, match_id):
        continue

    detail_url = f"https://www.flashscore.pl/mecz/{match_id}/#/szczegoly-meczu/statystyki-meczu/0"
    driver.get(detail_url)

    time.sleep(2)

    detail_page_source = driver.page_source
    detail_soup = BeautifulSoup(detail_page_source, 'html.parser')

    stats_rows = detail_soup.find_all('div', class_='_row_18zuy_8')

    stats = {}
    if stats_rows:
        for stat in stats_rows:
            category_name = stat.find('div', class_='_category_1haer_4').get_text(strip=True)
            if category_name in desired_stats:
                home_stat_value = stat.find('div', class_='_homeValue_7ptpb_9').get_text(strip=True)
                away_stat_value = stat.find('div', class_='_awayValue_7ptpb_13').get_text(strip=True)

                try:
                    home_value = float(home_stat_value.replace('%', '').strip())
                    away_value = float(away_stat_value.replace('%', '').strip())
                except ValueError:
                    home_value = 0.0
                    away_value = 0.0

                stats[category_name] = (home_value, away_value)

    add_match_to_db(c, match_id, home_team, away_team, goals_home_team, goals_away_team, stats)

conn.commit()
conn.close()

driver.quit()
