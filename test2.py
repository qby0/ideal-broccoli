import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import hashlib

# URL страницы, которую будем скрапить
base_url = "https://slovak.statistics.sk/"

# Выполняем GET-запрос
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

visited_links = set()
to_visit_links = [base_url]
visited_files = set()
blacklist_links = set()

# Функция для генерации уникального идентификатора файла на основе содержимого
def generate_file_id(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]

# Функция для сохранения таблицы в Excel
def save_table_to_excel(table, file_name):
    headers = [header.text.strip() for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr'):
        columns = row.find_all('td')
        row_data = [col.text.strip() for col in columns]
        if row_data:
            rows.append(row_data)
    # Проверяем, если таблица имеет только 2 колонки, игнорируем её
    if len(headers) == 2:
        print("Таблица имеет только 2 колонки, пропускаем.")
        return
    # Проверяем, есть ли заголовки, если нет, создаем пустой список заголовков для DataFrame
    if not headers:
        headers = [f"Column {i+1}" for i in range(len(rows[0]))]
    
    # Проверяем на несоответствие количества заголовков и данных
    if len(headers) != len(rows[0]):
        print("Несоответствие количества заголовков и данных, пропускаем таблицу.")
        return
    
    df = pd.DataFrame(rows, columns=headers)
    
    # Генерируем хеш от содержимого таблицы, чтобы определить уникальность файла
    content = df.to_csv(index=False)
    file_id = generate_file_id(content)
    final_file_name = file_name
    
    # Проверяем, существует ли файл с таким именем в директории, если да, добавляем индекс
    if os.path.exists(final_file_name):
        base_name, extension = os.path.splitext(file_name)
        index = 1
        while os.path.exists(final_file_name):
            final_file_name = f"{base_name}_{index}{extension}"
            index += 1
    
    df.to_excel(final_file_name, index=False)
    visited_files.add(final_file_name)
    print(f"Данные успешно сохранены в файл {final_file_name}")

# Функция для выполнения запроса и обработки ссылок
def scrape_page(url):
    if url in blacklist_links:
        print(f"Ссылка {url} в черном списке, пропускаем.")
        return
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if table:
            file_name = f"{url.split('/')[-2]}.xlsx"
            save_table_to_excel(table, file_name)
        for link in soup.find_all('a', href=True):
            full_url = link['href']
            if full_url.startswith('/'):
                full_url = "https://finstat.sk" + full_url
            # Игнорируем ссылки, которые начинаются с "mailto"
            if not full_url.startswith('mailto:') and "finstat.sk" in full_url and full_url not in visited_links:
                if full_url not in blacklist_links:
                    to_visit_links.append(full_url)
    else:
        print(f"Ошибка при запросе к странице {url}. Статус-код: {response.status_code}")
        blacklist_links.add(url)

# Основной цикл для обхода всех ссылок
while to_visit_links:
    current_url = to_visit_links.pop(0)
    if current_url not in visited_links:
        visited_links.add(current_url)
        scrape_page(current_url)

print("Скрапинг завершен.")
