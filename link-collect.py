import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

def scrape_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = { 
            'Predmet': '',
            'Cena': '',
            'Datum zver': '',
            'Strana 1 (objednavatel)': '',
            'Strana 1 ico': '',
            'Strana 2 (dodavatel)': '',
            'Strana 2 ico': ''
        }
        
        # Способ 1: Поиск <strong> с классом, содержащим 'text-danger' и символ евро
        cena_tag = soup.find('strong', class_=lambda x: x and 'text-danger' in x and '€' in x)
        if cena_tag:
            # Извлечь текстовую часть, содержащую цену
            data['Cena'] = cena_tag.get_text(strip=True)
        else:
            # Способ 2: Поиск по тексту, содержащему символ евро
            cena_tag = soup.find('strong', string=lambda text: text and '€' in text)
            if cena_tag:
                data['Cena'] = cena_tag.get_text(strip=True)
        
        # Если цена все еще не найдена, можно попытаться найти по метке
        if not data['Cena']:
            cena_label = soup.find('strong', string=lambda text: text and 'Celková čiastka' in text)
            if cena_label:
                cena_value = cena_label.find_next_sibling(text=True)
                if cena_value:
                    data['Cena'] = cena_value.strip()
        
        # Найти все элементы со списком данных
        list_items = soup.find_all('li', class_='py-2')
        
        current_label = None
        for item in list_items:
            strong = item.find('strong')
            if strong:
                label = strong.get_text(strip=True).rstrip(':')
                span = strong.find_next_sibling('span')
                value = span.get_text(strip=True) if span else ''
                
                if label == 'Názov zmluvy':
                    data['Predmet'] = value
                elif label == 'Dátum zverejnenia':
                    data['Datum zver'] = value
                elif label == 'Objednávateľ':
                    data['Strana 1 (objednavatel)'] = value
                elif label == 'IČO' and current_label == 'Objednávateľ':
                    data['Strana 1 ico'] = value
                elif label == 'Dodávateľ':
                    data['Strana 2 (dodavatel)'] = value
                elif label == 'IČO' and current_label == 'Dodávateľ':
                    data['Strana 2 ico'] = value
                
                current_label = label
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f'Ошибка при запросе {url}: {e}')
        return None

if __name__ == "__main__":
    data_list = []
    
    with open('links.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                url = row[0].strip()
                # Проверка формата URL
                if url.startswith('https://www.crz.gov.sk/zmluva/'):
                    print(f'Обработка URL: {url}')
                    result = scrape_data(url)
                    if result:
                        data_list.append(result)
                        for key, value in result.items():
                            print(f"{key}: {value}")
                        print('-' * 40)
                else:
                    print(f'Пропуск URL (не соответствует формату): {url}')
    
    # Проверка наличия данных перед сохранением
    if data_list:
        # Создать DataFrame и сохранить в Excel
        df = pd.DataFrame(data_list)
        df.to_excel('output.xlsx', index=False)
        print('Данные сохранены в output.xlsx')
    else:
        print('Нет данных для сохранения.')