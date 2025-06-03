import os
import subprocess
import rasterio
import numpy as np
import matplotlib.pyplot as plt

#  Визначаємо основні папки
base_dir = r"C:\Dediaieva\AD\labs\lab7"             # Папка з лабораторною роботою
data_dir = os.path.join(base_dir, "data")           # Папка з вхідними файлами
shapefile_dir = os.path.join(base_dir, "lab 7 data")  # Папка з шейпфайлом (границями)
processed_dir = os.path.join(data_dir, "processed") # Папка, куди зберігатимуться оброблені файли
os.makedirs(processed_dir, exist_ok=True)           # Якщо папки немає — створити

# Визначаємо шляхи до файлів з каналами Sentinel-2
sentinel_b2 = os.path.join(data_dir, "Sentinel-2_L2A_B02.tiff")  # Канал Blue (синій)
sentinel_b3 = os.path.join(data_dir, "Sentinel-2_L2A_B03.tiff")  # Канал Green (зелений)
sentinel_b4 = os.path.join(data_dir, "Sentinel-2_L2A_B04.tiff")  # Канал Red (червоний)
sentinel_b8 = os.path.join(data_dir, "Sentinel-2_L2A_B08.tiff")  # Канал Near Infrared (близький інфрачервоний)
shapefile_path = os.path.join(shapefile_dir, "Kyiv_regions.shp")  # Полігон (контур) Києва для обрізки

#  1. Об'єднуємо окремі канали в одне RGB-зображення
def combine_rgb_channels(input_files, output_path):
    print("Об'єднання каналів у RGB зображення...")
    # Викликаємо зовнішній скрипт gdal_merge.py, який збирає вхідні канали у багатошарове TIFF з трьома каналами (RGB)
    subprocess.run(["python", "gdal_merge.py", "-separate", "-o", output_path] + input_files, shell=True, check=True)

# 2. Змінюємо систему координат (репроекція) на більш звичну географічну (широта, довгота)
def reproject_to_wgs84(input_file, output_file):
    print("Репроекція у WGS84...")
    # Використовуємо gdalwarp для перетворення координат
    subprocess.run(["gdalwarp", "-s_srs", "EPSG:32633", "-t_srs", "EPSG:4326", input_file, output_file], shell=True, check=True)

#  3. Об'єднуємо RGB та NIR канали в один файл (4 шари)
def combine_all_channels(input_files, output_path):
    print("Об’єднання RGB + NIR...")
    # Знову gdal_merge.py, але тепер з 4-ма каналами
    subprocess.run(["python", "gdal_merge.py", "-separate", "-o", output_path] + input_files, shell=True, check=True)

#  4. Обрізка зображення по полігону із шейпфайлу
def clip_by_shapefile(input_file, shapefile, output_file):
    print("Обрізка по shapefile...")
    # Якщо результат вже існує, видаляємо старий файл, щоб не було помилок
    if os.path.exists(output_file):
        os.remove(output_file)
    # Обрізаємо зображення, щоб залишити лише ту частину, яка належить Києву (за межами обрізки видалиться)
    subprocess.run(["gdalwarp", "-cutline", shapefile, "-crop_to_cutline", input_file, output_file], shell=True, check=True)
    # Перевіряємо скільки каналів в обрізаному файлі
    with rasterio.open(output_file) as src:
        print(f"Кількість каналів: {src.count}")

#  5. Візуалізація зображення
def display_image(image_file):
    with rasterio.open(image_file) as src:
        print(f"Кількість каналів: {src.count}")
        # Читаємо перші три канали, або один, якщо менше трьох
        img = src.read([1, 2, 3]).astype(np.float32) if src.count >= 3 else src.read(1).astype(np.float32)
        # Переставляємо розміри так, щоб колірні канали були останнім виміром (для plt.imshow)
        img = np.moveaxis(img, 0, -1)
        # Масштабуємо значення пікселів від 0 до 1 для коректного відображення
        img = (img - img.min()) / (img.max() - img.min()) if img.max() != img.min() else np.zeros_like(img)
    # Відображаємо зображення
    plt.figure(figsize=(10, 10))
    plt.imshow(img)
    plt.title(os.path.basename(image_file))  # Відображаємо ім'я файлу у заголовку
    plt.axis("off")                         # Прибираємо осі для чистого вигляду
    plt.show()

#  6. Паншарпінг (покращення якості RGB за допомогою інфрачервоного каналу)
def perform_pansharpening(rgb_input, pan_input, output_file, method):
    print(f"Паншарпінг методом {method}...")
    # Тут виконуємо ресемплінг (зміна роздільності) з різними методами (bilinear, cubic і т.д.)
    subprocess.run(["gdalwarp", "-r", method, rgb_input, pan_input, output_file], shell=True, check=True)

#  Файли для збереження результатів
rgb_output = os.path.join(processed_dir, "Sentinel-2_RGB.tif")               # RGB зображення
reproj_output = os.path.join(processed_dir, "Sentinel-2_RGB_reprojected.tif")  # Репроекція RGB
full_output = os.path.join(processed_dir, "Sentinel-2_RGBNIR.tif")            # RGB + NIR
clipped_output = os.path.join(processed_dir, "Sentinel-2_Clipped.tif")        # Обрізане по шейпфайлу

#  Послідовність виконання
combine_rgb_channels([sentinel_b2, sentinel_b3, sentinel_b4], rgb_output)  # Зібрати RGB
reproject_to_wgs84(rgb_output, reproj_output)                             # Змінити проекцію
combine_all_channels([sentinel_b2, sentinel_b3, sentinel_b4, sentinel_b8], full_output)  # Додати NIR
clip_by_shapefile(full_output, shapefile_path, clipped_output)            # Обрізати по Києву
display_image(clipped_output)                                            # Показати обрізане зображення

# Методи паншарпінгу, які перевіряємо
methods = ["bilinear", "cubic", "lanczos", "average"]
for method in methods:
    pan_output = os.path.join(processed_dir, f"Sentinel-2_Pansharpened_{method}.tif")
    perform_pansharpening(rgb_output, sentinel_b8, pan_output, method)  # Застосувати паншарпінг
    display_image(pan_output)                                         # Показати результат

print("Всі етапи обробки завершені.")



