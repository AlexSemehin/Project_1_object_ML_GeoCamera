#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from os import listdir, path, makedirs
from pathlib import Path
import numpy as np
import pandas as pd
from geopandas import GeoDataFrame, gpd
from shapely.geometry import Point, LineString
import torch
import time
from PIL import Image
from ultralytics import YOLO
import sys
from tkinter import Tk, Label, Entry, Button, messagebox, Text, NORMAL, END, DISABLED
from tkinter import filedialog, ttk

def convert_posc_to_dataframe(folder_path):
    posc_files = [f for f in os.listdir(folder_path) if f.endswith('.PosC')]
    if not posc_files:
        print("Нет файлов с расширением .PosC в указанной папке.")
        return pd.DataFrame()
    
    combined_data = pd.DataFrame()
    for posc_file in posc_files:
        posc_file_path = os.path.join(folder_path, posc_file)
        try:
            data = pd.read_csv(posc_file_path, sep=' ')
            if 'Name' in data.columns:
                data.rename(columns={'Name': 'filename'}, inplace=True)
            else:
                print(f'Столбец "Name" не найден в файле {posc_file}.')
            combined_data = pd.concat([combined_data, data], ignore_index=True)
            print(f'Файл {posc_file} успешно обработан.')
        except Exception as e:
            print(f'Ошибка при обработке файла {posc_file}: {e}')
    return combined_data

def load_model(model_path):
    if not os.path.isfile(model_path):
        print(f"Файл модели '{model_path}' не найден.")
        return None
    try:
        model = YOLO(model_path)
        print("Модель успешно загружена.")
        return model
    except Exception as e:
        print(f"Ошибка при загрузке модели: {e}")
        return None

def predict_image(model, image_file):
    start_time = time.time()
    try:
        img = Image.open(image_file).convert("RGB")
        predictions = model.predict(img)

        results = predictions[0]
        predicted_classes = [model.names[int(box.cls[0])] for box in results.boxes] if results.boxes else []
        boxes = results.boxes.xyxy.cpu().numpy() if results.boxes else []

        coordinates = {
            'distance_mark': [],
            'crossing': []
        }
        for box, cls in zip(boxes, predicted_classes):
            if cls == 'distance_mark':
                coordinates['distance_mark'].append(box)
            elif cls == 'crossing':
                coordinates['crossing'].append(box)

        result = {
            'filename': image_file.name,
            'dist_mark': 'distance_mark' in predicted_classes,
            'crossing': 'crossing' in predicted_classes,
            'time_taken': time.time() - start_time
        }

        for i, box in enumerate(coordinates['distance_mark'], start=1):
            x1, y1, x2, y2 = box
            result[f'distance_mark_coords_{i}'] = f"{x1},{y1},{x2},{y2}"

        for i, box in enumerate(coordinates['crossing'], start=1):
            x1, y1, x2, y2 = box
            result[f'crossing_coords_{i}'] = f"{x1},{y1},{x2},{y2}"

        return result
    except Exception as e:
        print(f"Ошибка при обработке предсказания для {image_file.name}: {e}")
        result = {
            'filename': image_file.name,
            'dist_mark': False,
            'crossing': False,
            'time_taken': time.time() - start_time
        }
        return result

def create_line_shapefile(df, output_folder):
    if 'Latitude(deg)' not in df.columns or 'Longitude(deg)' not in df.columns:
        print("DataFrame должен содержать колонки 'Latitude(deg)' и 'Longitude(deg)'.")
        return
    
    if 'GPSTime(sec)' in df.columns:
        df = df.sort_values(by='GPSTime(sec)')
    
    points = [Point(row['Longitude(deg)'], row['Latitude(deg)']) for _, row in df.iterrows()]
    
    if len(points) > 1:
        line = LineString(points)
        gdf_line = gpd.GeoDataFrame(geometry=[line], crs='EPSG:4326')
        shapefile_output_line = os.path.join(output_folder, 'track.shp')
        gdf_line.to_file(shapefile_output_line, driver='ESRI Shapefile', encoding='utf-8')
        print(f"Shapefile для трека успешно сохранен: {shapefile_output_line}")
    else:
        print("Недостаточно точек для создания линии.")

def csv_to_shapefiles(folder_path, output_folder):
    csv_file = os.path.join(folder_path, 'road_signs.csv')
    if not os.path.isfile(csv_file):
        print(f"Файл '{csv_file}' не найден.")
        return
    
    df = pd.read_csv(csv_file)

    required_columns = ['Latitude(deg)', 'Longitude(deg)', 'dist_mark', 'crossing', 'filename', 'GPSTime(sec)']
    if not all(col in df.columns for col in required_columns):
        print("CSV файл должен содержать колонки 'Latitude(deg)', 'Longitude(deg)', 'dist_mark', 'crossing', 'filename', 'GPSTime(sec)'.")
        return
    
    df['dist_mark'] = df['dist_mark'].map({'True': True, 'False': False, 1: True, 0: False}).fillna(False)
    df['crossing'] = df['crossing'].map({'True': True, 'False': False, 1: True, 0: False}).fillna(False)

    df_dm_filtered = df[df['dist_mark'] == True]
    if not df_dm_filtered.empty:
        dm_points = []
        dm_attributes = []
        for _, row in df_dm_filtered.iterrows():
            dm_points.append(Point(row['Longitude(deg)'], row['Latitude(deg)']))
            dm_attributes.append({
                'filename': row['filename'],
                'GPSTime': row['GPSTime(sec)']
            })
            for i in range(2, 4):
                col_name = f'distance_mark_coords_{i}'
                if col_name in row and pd.notna(row[col_name]):
                    coords = row[col_name].split(',')
                    if len(coords) == 4:
                        x1, y1, x2, y2 = map(float, coords)
                        dm_points.append(Point((x1 + x2) / 2, (y1 + y2) / 2))
                        dm_attributes.append({
                            'filename': row['filename'],
                            'GPSTime': row['GPSTime(sec)']
                        })

        if dm_points:
            gdf_dm = gpd.GeoDataFrame(dm_attributes, geometry=dm_points, crs='EPSG:4326')
            shapefile_output_dm = os.path.join(output_folder, 'distance_mark.shp')
            gdf_dm.to_file(shapefile_output_dm, driver='ESRI Shapefile', encoding='utf-8')
            print(f"Shapefile для distance_mark успешно сохранен: {shapefile_output_dm}")
        else:
            print("Нет координат для distance_mark.")
    else:
        print("Нет данных с 'dist_mark' = True.")

    df_c_filtered = df[df['crossing'] == True]
    if not df_c_filtered.empty:
        c_points = []
        c_attributes = []

        for _, row in df_c_filtered.iterrows():
            c_points.append(Point(row['Longitude(deg)'], row['Latitude(deg)']))
            c_attributes.append({
                'filename': row['filename'],
                'GPSTime': row['GPSTime(sec)']
            })

            for i in range(2, 4):
                col_name = f'crossing_coords_{i}'
                if col_name in row and pd.notna(row[col_name]):
                    c_points.append(Point(row['Longitude(deg)'], row['Latitude(deg)']))
                    c_attributes.append({
                        'filename': row['filename'],
                        'GPSTime': row['GPSTime(sec)']
                    })

            for i in range(1, 4):
                col_name = f'distance_mark_coords_{i}'
                if col_name in row and pd.notna(row[col_name]):
                    c_points.append(Point(row['Longitude(deg)'], row['Latitude(deg)']))
                    c_attributes.append({
                        'filename': row['filename'],
                        'GPSTime': row['GPSTime(sec)']
                    })

        if c_points:
            gdf_c = gpd.GeoDataFrame(c_attributes, geometry=c_points, crs='EPSG:4326')
            shapefile_output_c = os.path.join(output_folder, 'crossing.shp')
            gdf_c.to_file(shapefile_output_c, driver='ESRI Shapefile', encoding='utf-8')
            print(f"Shapefile для crossing успешно сохранен: {shapefile_output_c}")
        else:
            print("Нет координат для crossing.")
    else:
        print("Нет данных с 'crossing' = True.")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ изображений")

        self.posc_folder = ""
        self.images_folder = ""
        self.output_folder = ""

        self.posc_label = Label(root, text="Папка с файлами .PosC:")
        self.posc_label.grid(row=0, column=0, padx=10, pady=10)

        self.posc_entry = Entry(root, width=50)
        self.posc_entry.grid(row=0, column=1, padx=10, pady=10)

        self.posc_button = Button(root, text="Выбрать", command=self.select_posc_folder)
        self.posc_button.grid(row=0, column=2, padx=10, pady=10)

        self.images_label = Label(root, text="Папка с изображениями:")
        self.images_label.grid(row=1, column=0, padx=10, pady=10)

        self.images_entry = Entry(root, width=50)
        self.images_entry.grid(row=1, column=1, padx=10, pady=10)

        self.images_button = Button(root, text="Выбрать", command=self.select_images_folder)
        self.images_button.grid(row=1, column=2, padx=10, pady=10)

        self.output_label = Label(root, text="Папка для сохранения результатов:")
        self.output_label.grid(row=2, column=0, padx=10, pady=10)

        self.output_entry = Entry(root, width=50)
        self.output_entry.grid(row=2, column=1, padx=10, pady=10)

        self.output_button = Button(root, text="Выбрать", command=self.select_output_folder)
        self.output_button.grid(row=2, column=2, padx=10, pady=10)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.log_text = Text(root, height=10, width=75)
        self.log_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.run_button = Button(root, text="Запустить", command=self.run_analysis)
        self.run_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        self.complete_button = Button(root, text="Завершить работу", command=self.root.quit, state=DISABLED)
        self.complete_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    def select_posc_folder(self):
        self.posc_folder = filedialog.askdirectory()
        self.posc_entry.delete(0, END)
        self.posc_entry.insert(0, self.posc_folder)

    def select_images_folder(self):
        self.images_folder = filedialog.askdirectory()
        self.images_entry.delete(0, END)
        self.images_entry.insert(0, self.images_folder)

    def select_output_folder(self):
        self.output_folder = filedialog.askdirectory()
        self.output_entry.delete(0, END)
        self.output_entry.insert(0, self.output_folder)

    def log(self, message):
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)

    def run_analysis(self):
        if not self.posc_folder or not self.images_folder or not self.output_folder:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите все папки.")
            return
        self.log("Начало обработки")
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            try:
                base_path = os.path.dirname(os.path.abspath(__file__))
            except NameError:
                base_path = "."
                self.log("Запуск в интерактивном режиме. Используется текущая папка.")

        posc_data = convert_posc_to_dataframe(self.posc_folder)
        model_path = os.path.join(base_path, 'best.pt')
        model = load_model(model_path)

        if model is None:
            messagebox.showerror("Ошибка", "Не удалось загрузить модель. Завершение работы.")
            return

        image_files = [img_file for img_file in Path(self.images_folder).glob("*") if
                       img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']]

        results = []
        self.progress["maximum"] = len(image_files)
        for i, image_file in enumerate(image_files):
            result = predict_image(model, image_file)
            results.append(result)
            self.progress["value"] = i + 1
            self.root.update_idletasks()
            self.log(f"Обработано изображение {image_file.name}")

        results_df = pd.DataFrame(results)

        if results_df.empty:
            messagebox.showinfo("Информация", "Нет результатов для отображения.")
            return

        output_folder = os.path.join(self.output_folder, "ML_Camera")
        os.makedirs(output_folder, exist_ok=True)

        csv_file_path = os.path.join(output_folder, "predictions.csv")
        results_df.to_csv(csv_file_path, index=False)

        self.log(f"Результаты сохранены в {csv_file_path}")

        posc_data['filename'] = posc_data['filename'].str.lower().str.strip().str.replace('.jpg', '', regex=False)
        results_df['filename'] = results_df['filename'].str.lower().str.strip().str.replace('.jpg', '', regex=False)

        if not posc_data.empty and not results_df.empty:
            combined_df = pd.merge(posc_data, results_df, on='filename', how='outer')
            if not combined_df.empty:
                output_csv_path = os.path.join(output_folder, "road_signs.csv")
                combined_df.to_csv(output_csv_path, index=False)
                self.log(f'Общий датафрейм успешно сохранен в {output_csv_path}')
            else:
                self.log("Нет совпадающих строк для объединения.")
        else:
            self.log("Нет данных для объединения.")

        create_line_shapefile(posc_data, output_folder)
        csv_to_shapefiles(output_folder, output_folder)

        self.complete_button.config(state=NORMAL)
        self.log("Анализ завершен. Нажмите 'Завершить работу' для выхода.")

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()


# In[ ]:




