import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import re

def scrape_links(base_url):
    all_links = set()
    page = 0
    pattern = re.compile(r'^/zmluva/\d+/$')
    
    while True:
        url = f"{base_url}?page={page}"
        print(f'Обработка страницы: {url}')
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Ошибка при запросе {url}: {e}')
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='table_list')
        
        if not table:
            print('Таблица не найдена. Завершение сбора ссылок.')
            break  # Выход, если таблица не найдена
        
        rows = table.find('tbody').find_all('tr')
        if not rows:
            print('Нет строк в таблице. Завершение сбора ссылок.')
            break
        
        for row in rows:
            link_tag = row.find('a', href=pattern)
            if link_tag:
                href = link_tag.get('href')
                full_url = urljoin(base_url, href)
                all_links.add(full_url)
                print(f'Найдена ссылка: {full_url}')
        
        # Проверка, есть ли переход на следующую страницу
        pagination = soup.find('nav', role='navigation', attrs={'aria-label': 'Strankovanie'})
        if not pagination:
            print('Пагинация не найдена. Завершение сбора ссылок.')
            break
        
        next_page = pagination.find('a', class_='page-link---next')
        if not next_page or 'href' not in next_page.attrs:
            print('Следующая страница отсутствует. Завершение сбора ссылок.')
            break
        
        page += 1

    return list(all_links)

if __name__ == "__main__":
    base_url = 'https://www.crz.gov.sk/6276460-sk/obec-vlkanova/'
    links = scrape_links(base_url)
    
    if links:
        with open('links.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for link in links:
                writer.writerow([link])
        print(f'Собрано {len(links)} ссылок. Сохранено в links.csv')
    else:
        print('Ссылки не найдены.')
