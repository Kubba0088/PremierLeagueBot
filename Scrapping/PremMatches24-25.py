from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Selenium - konfiguracja
driver_path = 'C:/webdriver/chromedriver-win64/chromedriver.exe'
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Strona z meczami
url = "https://www.flashscore.pl/pilka-nozna/anglia/premier-league/mecze/"
driver.get(url)

# Zbieranie źródła strony i parsowanie
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

# Zmienna do przechowywania HTML
html_content = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mecze Premier League</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h2 { color: #333; }
        .round { margin-bottom: 20px; }
        .match { margin-left: 20px; }
    </style>
</head>
<body>
    <h1>Mecze Premier League</h1>
'''

# Pobieranie rund i meczów
rounds = soup.find_all('div', class_='event__round event__round--static')

# Przetwarzanie każdej rundy
for round_div in rounds:
    round_title = round_div.get_text(strip=True)  # Tytuł rundy (np. "Kolejka 8")

    # Dodanie rundy do HTML
    html_content += f'<div class="round"><h2>{round_title}</h2>\n'

    # Znalezienie wszystkich meczów dla tej rundy
    next_sibling = round_div.find_next_sibling('div')

    while next_sibling and 'event__match' in next_sibling.get('class', []):
        home_team = next_sibling.find('div', class_='event__homeParticipant').get_text(strip=True)
        away_team = next_sibling.find('div', class_='event__awayParticipant').get_text(strip=True)
        date = next_sibling.find('div', class_='event__time').get_text(strip=True)

        # Dodanie meczu do HTML
        html_content += f'<div class="match">Data: {date} | Gospodarz: {home_team} | Gość: {away_team}</div>\n'

        # Przejdź do następnego meczu
        next_sibling = next_sibling.find_next_sibling('div')

    html_content += '</div>\n'  # Zakończenie sekcji rundy

# Zakończenie dokumentu HTML
html_content += '''
</body>
</html>
'''

# Zapisanie do pliku HTML
with open('mecze_premier_league.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

# Zamknięcie przeglądarki
driver.quit()
