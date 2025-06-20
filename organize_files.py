import os
import shutil
from datetime import datetime
import argparse

def get_creation_date(file_path):
    """Получает дату создания файла в формате YYYY-MM-DD"""
    try:
        stat = os.stat(file_path)
        timestamp = stat.st_birthtime if hasattr(stat, 'st_birthtime') else stat.st_ctime
    except AttributeError:
        timestamp = os.path.getmtime(file_path)
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

def get_file_category(extension):
    """Определяет категории файлов для особой обработки"""
    extension = extension.upper()
    
    # RAW-файлы
    raw_extensions = {'CR3', 'ARW', 'NEF', 'DNG', 'RAF'}
    if extension in raw_extensions:
        return 'RAW'
    
    # Видео файлы (будут в папке EXT/Оригиналы)
    video_extensions = {'MP4', 'MOV', 'AVI', 'MKV'}
    if extension in video_extensions:
        return os.path.join(extension, 'Оригиналы')
    
    return extension

def organize_files(source_dir, dest_dir, action='move'):
    """Организует файлы с учетом специальных правил"""
    for root, _, files in os.walk(source_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            
            if filename.startswith('.'):
                continue
                
            try:
                creation_date = get_creation_date(file_path)
                ext = os.path.splitext(filename)[1]
                
                if ext:
                    ext = ext[1:]  # Убираем точку
                    folder_name = get_file_category(ext)
                else:
                    folder_name = "NO_EXTENSION"
                
                # Создаем целевую директорию
                target_dir = os.path.join(dest_dir, creation_date, folder_name)
                os.makedirs(target_dir, exist_ok=True)
                
                # Обработка дубликатов
                base, ext = os.path.splitext(filename)
                target_path = os.path.join(target_dir, filename)
                counter = 1
                while os.path.exists(target_path):
                    new_name = f"{base}_{counter}{ext}"
                    target_path = os.path.join(target_dir, new_name)
                    counter += 1
                
                # Выполняем действие
                if action.lower() == 'copy':
                    shutil.copy2(file_path, target_path)
                    print(f"Скопирован: {file_path} -> {target_path}")
                else:
                    shutil.move(file_path, target_path)
                    print(f"Перемещен: {file_path} -> {target_path}")
                    
            except Exception as e:
                print(f"Ошибка при обработке {file_path}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Организация файлов с особыми правилами',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--source', default=os.getcwd(),
                       help='Исходная директория (например, /Volumes/FLASH)')
    parser.add_argument('--dest', default=os.getcwd(),
                       help='Целевая директория')
    parser.add_argument('--action', choices=['move', 'copy'], default='move',
                       help='Действие: move - переместить, copy - скопировать')
    
    args = parser.parse_args()
    
    source = os.path.abspath(os.path.expanduser(args.source))
    dest = os.path.abspath(os.path.expanduser(args.dest))
    
    print(f"Организация файлов из: {source}")
    print(f"В директорию: {dest}")
    print("\nПравила обработки:")
    print("- CR3, ARW, NEF → папка RAW")
    print("- MP4 → MP4/Оригиналы/")
    print("- MOV → MOV/Оригиналы/")
    print("- Остальные файлы → папки по расширению в UPPERCASE\n")
    
    organize_files(source_dir=source, dest_dir=dest, action=args.action)
    
    print("\nОбработка завершена!")