import pandas as pd
import os

# Получите текущую директорию
directory = os.getcwd()

# Получите список всех Excel файлов в директории
excel_files = [f for f in os.listdir(directory) if f.endswith(('.xlsx', '.xls'))]

# Создайте пустой DataFrame для объединения
combined_df = pd.DataFrame()

# Пройдитесь по каждому файлу и объедините данные
for file in excel_files:
    file_path = os.path.join(directory, file)
    df = pd.read_excel(file_path)
    combined_df = pd.concat([combined_df, df], ignore_index=True)

# Сохраните объединенный DataFrame в новый Excel файл
combined_df.to_excel(os.path.join(directory, 'combined.xlsx'), index=False)