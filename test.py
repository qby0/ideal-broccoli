import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL страницы, которую будем скрапить
url = "https://finstat.sk/00313271/vykaz_ziskov_strat"

# Выполняем GET-запрос
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)

# Проверяем успешность запроса
if response.status_code == 200:
    # Извлекаем содержимое страницы
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Ищем первую таблицу на странице
    table = soup.find('table')
    
    if table:
        # Извлекаем заголовки таблицы
        headers = [header.text.strip() for header in table.find_all('th')]
        
        # Извлекаем строки таблицы
        rows = []
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            row_data = [col.text.strip() for col in columns]
            if row_data:  # Только если строка не пустая
                rows.append(row_data)
        
        # Создаем DataFrame из заголовков и строк
        df = pd.DataFrame(rows, columns=headers)
        
        # Сохраняем DataFrame в Excel-файл
        df.to_excel('vykaz_ziskov_strat.xlsx', index=False)
        print("Данные успешно сохранены в файл vykaz_ziskov_strat.xlsx")
    else:
        print("Не удалось найти таблицу на странице.")
else:
    print(f"Ошибка при запросе к странице. Статус-код: {response.status_code}")
