import requests

from config import Config
import os
import shutil
import json
import time
import zipfile
import webbrowser

config_manager = Config(
    config={
        "path_to_game": "",
        "active_mods": {},
        "copied": "False",
        "first_setup": "False",
        "github_repo_url_get": "https://raw.githubusercontent.com/ANTIoffz/forts_in_build_mods/main/README.md",
        "download_mods_page_url": "https://catalogue.smods.ru/archives/category/mod?app=410900",
        "download_maps_page_url": "https://catalogue.smods.ru/archives/category/map?app=410900"
    }
)


def clear_console_screen():
    system_name = os.name
    if system_name == 'posix':
        command = 'clear'
    elif system_name == 'nt':
        command = 'cls'
    else:
        command = "\033c"
    os.system(command)


def validate_game_path(user_game_path: str) -> bool | str:
    if os.path.isfile(user_game_path) and os.path.basename(user_game_path) == 'Forts.exe':
        game_folder = os.path.dirname(user_game_path)
    elif os.path.exists(user_game_path):
        game_folder = user_game_path
    else:
        print('Некорректный путь')
        return False
    if not os.path.isfile(os.path.join(game_folder, "Forts.exe")):
        print('Игра не найдена')
        return False
    if not os.path.exists(f"{game_folder}\data\mods"):
        print("В каталоге игры не найдена папка mods")
        return False
    return game_folder


def delete_mods_menu():
    while True:
        clear_console_screen()
        active_mods = config_manager.read('active_mods')
        print("-- Удаление модов --")
        print("\n".join(f"{number + 1}: {mod_name}" for number, mod_name in enumerate(active_mods)))
        selected_mod_number = input()
        if not selected_mod_number:
            break

        try:
            selected_mod_name = list(active_mods.keys())[int(selected_mod_number) - 1]
            active_mods.pop(selected_mod_name)
            config_manager.update("active_mods", active_mods)
            print(selected_mod_name)
        except:
            continue


def add_mods_menu():
    while True:
        clear_console_screen()
        active_mods = config_manager.read('active_mods')
        all_mods = [x for x in os.listdir('mods') if x not in active_mods]
        all_in_game_mods = [x for x in os.listdir(f"{config_manager.read('path_to_game')}\data\mods") if
                            x not in active_mods.values()]
        print("-- Добавление модов --")
        print("\n".join(f"{mod_name} : {mod_replaced}" for mod_name, mod_replaced in active_mods.items()))
        print('''-----------------------''')
        print("\n".join(f"{number + 1}: {mod_name}" for number, mod_name in enumerate(all_mods)))
        selected_mod_number = input()
        if not selected_mod_number:
            break
        try:
            selected_mod_name = all_mods[int(selected_mod_number) - 1]
            while True:
                clear_console_screen()
                print(f"-- Замена на '{selected_mod_name}' --")
                print("\n".join(f"{number + 1}: {mod_name}" for number, mod_name in enumerate(all_in_game_mods)))

                selected_replacement_mod_number = input()
                if not selected_replacement_mod_number:
                    break
                try:
                    selected_replacement_mod_name = all_in_game_mods[int(selected_replacement_mod_number) - 1]
                    active_mods[selected_mod_name] = selected_replacement_mod_name
                    config_manager.update("active_mods", active_mods)
                    break
                except:
                    continue
        except:
            continue


def launch_game():
    game_folder = config_manager.read('path_to_game')
    active_mods = config_manager.read('active_mods')
    backuped_mods = os.listdir(f'backuped_mods')

    for number, mod_name in enumerate(backuped_mods):
        clear_console_screen()
        print("-- Не забудьте стим :D --")
        print(f'Копирование: {mod_name} | {number + 1} / {len(backuped_mods)}', end='\r')
        try:
            shutil.rmtree(f"{game_folder}/data/mods/{mod_name}")
        except:
            pass
        shutil.copytree(f"backuped_mods/{mod_name}", f"{game_folder}/data/mods/{mod_name}")

    clear_console_screen()
    print("-- Ожидание загрузки --")
    print("Нажмите ENTER когда игра запустится полностью")
    os.system(f"start {game_folder}/Forts.exe")
    input()

    for mod_name, backuping_mod_name in active_mods.items():
        clear_console_screen()
        print(f'Копирование: {mod_name}', end='\r')
        shutil.rmtree(f"{game_folder}/data/mods/{backuping_mod_name}")
        shutil.copytree(f"mods/{mod_name}", f"{game_folder}/data/mods/{backuping_mod_name}")
    clear_console_screen()
    print("Готово!")


def manage_modpacks():
    while True:
        clear_console_screen()
        modpacks_list = os.listdir("modpacks")
        print("-- Сборки модов --")
        print("\n".join(f"{number + 1}: {modpack_name}" for number, modpack_name in enumerate(modpacks_list)))
        print('')
        print('N | Создать сборку')
        modpack_choice = input().lower()
        if not modpack_choice:
            break

        if modpack_choice == "n":
            while True:
                clear_console_screen()
                print("-- Введите название --")
                modpack_name = input()
                if not modpack_name: break

                modpack_active_mods = config_manager.read('active_mods').keys()
                os.mkdir(f"modpacks/{modpack_name}")

                for number, mod_name in enumerate(modpack_active_mods):
                    clear_console_screen()
                    print(f'Копирование: {mod_name} | {number} / {len(modpack_active_mods)}', end='\r')
                    shutil.copytree(f"mods/{mod_name}", f'modpacks/{modpack_name}/mods/{mod_name}')

                with open(f'modpacks/{modpack_name}/config.json', "w", encoding='utf-8') as file:
                    json.dump(config_manager.read("active_mods"), file)

                break

        try:
            while True:
                clear_console_screen()
                selected_modpack_name = modpacks_list[int(modpack_choice) - 1]
                selected_modpack_config = Config(path=f'modpacks/{selected_modpack_name}/config.json')
                selected_modpack_mods = selected_modpack_config.read()
                print(f"-- {selected_modpack_name} --")
                print("\n".join(
                    f"{mod_name} : {mod_replaced}" for mod_name, mod_replaced in selected_modpack_mods.items()))
                print("")
                print("Y | Использовать")
                print("D | Удалить")
                selected_action = input().lower()
                if not selected_action:
                    break
                match selected_action:
                    case "y":
                        for number, mod_name in enumerate(selected_modpack_mods.keys()):
                            try:
                                clear_console_screen()
                                print(f'Копирование: {mod_name} | {number} / {len(selected_modpack_mods)}', end='\r')
                                shutil.copytree(f"modpacks/{selected_modpack_name}/mods/{mod_name}", f"mods/{mod_name}")
                            except:
                                pass
                        config_manager.update('active_mods', selected_modpack_mods)
                        break
                    case "d":
                        clear_console_screen()
                        print(f'Вы уверены что хотите удалить "{selected_modpack_name}"?')
                        print("Y | Да")
                        print("N | Нет")
                        if input().lower() == 'y':
                            shutil.rmtree(f"modpacks/{selected_modpack_name}")
                            break
                    case _:
                        continue
        except:
            continue


def prompt_user_for_game_path():
    while True:
        clear_console_screen()
        print("-- Путь к игре --")
        print("Укажите путь к папке с игрой: ", end='')
        user_selected_game_path = input()
        game_folder = validate_game_path(user_selected_game_path)
        if game_folder:
            return game_folder


def misc_menu():
    while True:
        clear_console_screen()
        active_mods = config_manager.read('active_mods')
        print("-- Дополнительно --")
        print("1 | Восстановить моды")
        print("2 | Скачать копию модов с сервера")
        print("3 | Настроить заново")
        print("4 | Скачать моды")
        print("5 | Скачать карты")

        choice = input().lower()
        if not choice:
            break
        match choice:
            case "1":
                config_manager.update('copied', 'False')
                backup_installed_mods()
            case "2":
                start_download_from_server()
            case "3":
                config_manager.update('copied', 'False')
                config_manager.update('first_setup', 'False')
                first_setup()
            case "4":
                webbrowser.open(config_manager.read("download_mods_page_url"))
            case "5":
                webbrowser.open(config_manager.read("download_maps_page_url"))
            case _:
                continue


def main_menu():
    while True:
        clear_console_screen()
        active_mods = config_manager.read('active_mods')
        print("-- Активные моды --")
        print("\n".join(f"{mod_name} : {mod_replaced}" for mod_name, mod_replaced in active_mods.items()))
        print('')
        print("A | Добавить мод")
        print("D | Удалить мод")
        print("P | Сборки модов")
        print("M | Дополнительно")
        print("S | Запуск игры")

        choice = input().lower()
        match choice:
            case "a":
                add_mods_menu()
            case "d":
                delete_mods_menu()
            case "p":
                manage_modpacks()
            case "m":
                misc_menu()
            case "s":
                launch_game()
            case _:
                continue


def create_required_folders():
    folders = ['mods', 'backuped_mods', 'modpacks']
    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)


def initialize_game_path():
    valid_game_folder = config_manager.read('path_to_game')
    if validate_game_path(str(valid_game_folder)):
        return
    valid_game_folder = prompt_user_for_game_path()
    config_manager.update('path_to_game', valid_game_folder)


def backup_installed_mods():
    game_path = config_manager.read('path_to_game')
    in_game_mods = os.listdir(f'{game_path}/data/mods')
    for number, mod_name in enumerate(in_game_mods):
        clear_console_screen()
        print(f'Копирование: {mod_name} | {number + 1} / {len(in_game_mods)}', end='\r')

        try:
            shutil.rmtree(f"backuped_mods/{mod_name}")
        except:
            pass

        try:
            shutil.copytree(f"{game_path}/data/mods/{mod_name}", f"backuped_mods/{mod_name}")
        except:
            print(f"Ошибка при копировании {mod_name}")

    config_manager.update("copied", "True")


def download_file(
        repo_url: str,
        download_filename: str,
        extract_to: str = '',
        folder_from_move: str = ''
):
    clear_console_screen()
    print("-- Загрузка --")
    response = requests.get(repo_url, stream=True)

    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        try:
            total_size_MB = total_size / (1024 * 1024)
        except:
            total_size_MB = 0
        block_size = 1024
        bytes_downloaded = 0

        with open(download_filename, 'wb') as file:
            for data in response.iter_content(chunk_size=block_size):
                file.write(data)
                bytes_downloaded += len(data)
                megabytes_size = bytes_downloaded / (1024 * 1024)
                print(f"Загружено: {megabytes_size:.2f} / {total_size_MB:.2f} МБ", end='\r')

        with zipfile.ZipFile(download_filename, 'r') as zip_file:
            clear_console_screen()
            print("-- Извлечение --")
            file_list = zip_file.namelist()
            with zipfile.ZipFile(download_filename, 'r') as zip_file:
                for count, item in enumerate(zip_file.namelist()):
                    try:
                        shutil.rmtree(f"{extract_to}/{item}")
                    except:
                        pass
                    zip_file.extract(item, extract_to)
                    print(f"Извлечено {count} / {len(file_list)}", end='\r')

        # all_mods = os.listdir(folder_from_move)
        # for number, mod_name in enumerate(all_mods):
        #     clear_console_screen()
        #     print(f'Перенос: {mod_name} | {number + 1} / {len(all_mods)}', end='\r')
        #     try:
        #         shutil.rmtree(f"backuped_mods/{mod_name}")
        #     except:
        #         pass
        #     shutil.move(f"{folder_from_move}/{mod_name}", f"backuped_mods/{mod_name}")

        clear_console_screen()
        print("-- Очистка --")
        print("Удаляем остатки >:)")
        os.remove(download_filename)
        # os.rmdir(folder_from_move)
        clear_console_screen()
        return True
    else:
        clear_console_screen()
        print("-- Ошибка --")
        print(f"Произошла ошибка при скачивании. Статус: {response.status_code}")
        input()
        return False


def start_download_from_server():
    github_repo_url = requests.get(config_manager.read('github_repo_url_get')).text.strip()
    clear_console_screen()
    print(f"Получена ссылка: {github_repo_url}")
    time.sleep(0.5)
    status = download_file(
        github_repo_url,
        'forts_in_build_mods.zip',
        extract_to='backuped_mods'
    )
    if not status:
        raise KeyboardInterrupt


def first_setup():
    while True:
        clear_console_screen()
        print("-- Начальная настройка --")
        print("На этом этапе у вас не должно быть установлено никаких модов, кроме встроенных")
        print("Пожалуйста, проверьте что игра запускается без ошибок!")
        print()
        print("Y | Всё работает")
        print("N | Данные повреждены")
        selected_action = input().lower()
        if selected_action == 'y':
            backup_installed_mods()

        elif selected_action == 'n':
            while True:
                clear_console_screen()
                print("-- Скачивание с сервера --")
                print("Хотите попробовать скачать данные с сервера?")
                print()
                print("Y | Да")
                print("N | Нет")
                selected_action = input().lower()
                if selected_action == 'y':
                    start_download_from_server()
                    print("-- Проверка --")
                    print('Попробуйте запустить игру выбрав пункт "S" в главном меню')
                    print("Если игра не будет запускаться, переустановите её")
                    input("*ENTER*")
                    break


                elif selected_action == 'n':
                    clear_console_screen()
                    print("-- Тогда... --")
                    print("Пожалуйста, переустановите игру")
                    input()
                    raise KeyboardInterrupt

                else:
                    continue
        else:
            continue

        break
    config_manager.update("first_setup", "True")
    config_manager.update("copied", "True")


def start():
    create_required_folders()
    initialize_game_path()
    if config_manager.read("first_setup") != 'True':
        first_setup()
    if config_manager.read("copied") != 'True':
        backup_installed_mods()
    main_menu()


def main():
    try:
        start()
    except KeyboardInterrupt:
        clear_console_screen()
        print("--   :D   --")
        time.sleep(0.5)


if __name__ == '__main__':
    main()
