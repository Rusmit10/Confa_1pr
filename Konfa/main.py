import shlex
import sys
import os
import argparse


class VFSEmulator:
    def __init__(self, vfs_path=None, startup_script=None):
        self.vfs_name = "myvfs"
        self.current_path = "/"
        self.running = True
        self.vfs_path = vfs_path
        self.startup_script = startup_script
        self.command_history = []

        # Загрузка VFS из директории или использование стандартной
        if vfs_path:
            self.load_vfs_from_directory(vfs_path)
        else:
            self._init_default_filesystem()

        print("=== Параметры запуска ===")
        print(f"vfs_path: {self.vfs_path}")
        print(f"startup_script: {self.startup_script}")
        print(f"Загружено объектов: {len(self.filesystem)}")
        print("========================")
        print()

    def _init_default_filesystem(self):
        """Стандартная файловая система с большей структурой"""
        self.filesystem = {
            "/": {"type": "dir", "children": ["home", "etc", "var", "tmp"]},
            "/home": {"type": "dir", "children": ["user1", "user2", "guest"]},
            "/etc": {"type": "dir", "children": ["config.txt", "hosts"]},
            "/var": {"type": "dir", "children": ["log"]},
            "/tmp": {"type": "dir", "children": []},
            "/home/user1": {"type": "dir", "children": ["documents", "file1.txt", "file2.txt"]},
            "/home/user2": {"type": "dir", "children": ["downloads", "notes.txt"]},
            "/home/guest": {"type": "dir", "children": []},
            "/var/log": {"type": "dir", "children": ["system.log", "app.log"]},
            "/home/user1/documents": {"type": "dir", "children": ["report.doc", "data.txt"]},
            "/home/user2/downloads": {"type": "dir", "children": []},
            "/etc/config.txt": {"type": "file", "content": "setting1=value1\nsetting2=value2\n"},
            "/etc/hosts": {"type": "file", "content": "127.0.0.1 localhost\n"},
            "/home/user1/file1.txt": {"type": "file", "content": "Это содержимое file1.txt\nСтрока 2\nСтрока 3\n"},
            "/home/user1/file2.txt": {"type": "file", "content": "Файл 2 содержимое\nТестовая строка\n"},
            "/home/user2/notes.txt": {"type": "file", "content": "Заметки:\n1. Сделать покупки\n2. Позвонить\n"},
            "/var/log/system.log": {"type": "file",
                                    "content": "2024-01-15 10:00:00 Система запущена\n2024-01-15 10:05:00 Пользователь вошел\n"},
            "/var/log/app.log": {"type": "file", "content": "App started\nProcessing data\n"},
            "/home/user1/documents/report.doc": {"type": "file", "content": "Отчет за январь\nВыполнены все задачи\n"},
            "/home/user1/documents/data.txt": {"type": "file", "content": "123\n456\n789\n"},
        }

    def load_vfs_from_directory(self, directory_path):
        """Загрузка VFS из директории на диске (Этап 3)"""
        if not os.path.exists(directory_path):
            print(f"Ошибка: путь '{directory_path}' не существует")
            self._init_default_filesystem()
            return False

        if not os.path.isdir(directory_path):
            print(f"Ошибка: '{directory_path}' не является директорией")
            self._init_default_filesystem()
            return False

        self.filesystem = {}
        self._scan_directory(directory_path, "/")
        print(f"VFS загружена из '{directory_path}'")
        return True

    def _scan_directory(self, real_path, vfs_path):
        """Рекурсивное сканирование директории"""
        try:
            # Создаем запись для текущей директории
            self.filesystem[vfs_path] = {"type": "dir", "children": []}

            for item in os.listdir(real_path):
                real_item_path = os.path.join(real_path, item)
                vfs_item_path = f"{vfs_path}/{item}" if vfs_path != "/" else f"/{item}"

                if os.path.isdir(real_item_path):
                    # Это директория
                    self.filesystem[vfs_path]["children"].append(item)
                    self._scan_directory(real_item_path, vfs_item_path)
                else:
                    # Это файл
                    self.filesystem[vfs_path]["children"].append(item)
                    try:
                        with open(real_item_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(10000)  # Читаем до 10000 символов
                    except:
                        content = "[бинарные данные]"
                    self.filesystem[vfs_item_path] = {"type": "file", "content": content}
        except Exception as e:
            print(f"Ошибка сканирования {real_path}: {e}")

    def print_prompt(self):
        print(f"{self.vfs_name}:{self.current_path}$ ", end="", flush=True)

    def parse_input(self, user_input):
        try:
            parts = shlex.split(user_input.strip())
            if not parts:
                return None, []
            return parts[0], parts[1:]
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            return None, []

    def execute_command(self, command, args, original_input):
        self.command_history.append(original_input)

        if command == "exit":
            return self.exit_command(args, original_input)
        elif command == "ls":
            return self.ls_command(args, original_input)
        elif command == "cd":
            return self.cd_command(args, original_input)
        elif command == "conf-dump":
            return self.conf_dump_command(args, original_input)
        elif command == "run-script":
            return self.run_script_command(args, original_input)
        elif command == "list-scripts":
            return self.list_scripts_command(args, original_input)
        elif command == "pwd":
            return self.pwd_command(args, original_input)
        elif command == "mkdir":
            return self.mkdir_command(args, original_input)
        elif command == "touch":
            return self.touch_command(args, original_input)
        elif command == "history":
            return self.history_command(args, original_input)
        elif command == "cat":  # Новая команда для Этапа 4
            return self.cat_command(args, original_input)
        elif command == "find":  # Новая команда для Этапа 4
            return self.find_command(args, original_input)
        elif command == "tac":  # Новая команда для Этапа 4
            return self.tac_command(args, original_input)
        else:
            print(f"{command}: команда не найдена")
            return False

    def exit_command(self, args, original_input):
        if len(args) > 1:
            print("exit: слишком много аргументов")
            return False

        if len(args) == 1:
            try:
                int(args[0])
            except ValueError:
                print("exit: неверный код выхода")
                return False

        self.running = False
        print("Выход из эмулятора VFS")
        return True

    def _normalize_path(self, path):
        """Нормализация пути"""
        if not path or path == ".":
            return self.current_path

        if path.startswith("/"):
            normalized = path
        elif path == "..":
            if self.current_path == "/":
                return "/"
            parts = [p for p in self.current_path.split("/") if p]
            if parts:
                parts.pop()
                return "/" + "/".join(parts) if parts else "/"
            return "/"
        else:
            if self.current_path == "/":
                normalized = f"/{path}"
            else:
                normalized = f"{self.current_path}/{path}"

        # Убираем двойные слеши
        while "//" in normalized:
            normalized = normalized.replace("//", "/")

        return normalized

    def ls_command(self, args, original_input):
        long_format = False
        target_path = self.current_path

        if args:
            if "-l" in args:
                long_format = True
                args = [arg for arg in args if arg != "-l"]

            if args:
                if len(args) > 1:
                    print("ls: слишком много аргументов")
                    return False
                target_path = self._normalize_path(args[0])

        if target_path not in self.filesystem or self.filesystem[target_path]["type"] != "dir":
            print(f"ls: невозможно получить доступ к '{target_path}': Нет такой директории")
            return False

        children = self.filesystem[target_path]["children"]

        print(f"Содержимое директории {target_path}:")

        for item in children:
            item_path = f"{target_path}/{item}" if target_path != "/" else f"/{item}"
            if item_path not in self.filesystem:
                continue

            if long_format:
                item_type = "d" if self.filesystem[item_path]["type"] == "dir" else "-"
                size = len(self.filesystem[item_path].get("content", "")) if self.filesystem[item_path][
                                                                                 "type"] == "file" else 0
                print(f"{item_type}rw-r--r-- 1 user user {size:>6} Jan 15 12:00 {item}")
            else:
                item_suffix = "/" if self.filesystem[item_path]["type"] == "dir" else ""
                print(f"  {item}{item_suffix}")
        return True

    def cd_command(self, args, original_input):
        if len(args) > 1:
            print("cd: слишком много аргументов")
            return False

        new_path = args[0] if args else "/"
        target_path = self._normalize_path(new_path)

        if target_path not in self.filesystem or self.filesystem[target_path]["type"] != "dir":
            print(f"cd: {new_path}: Нет такой директории")
            return False

        self.current_path = target_path
        return True

    def cat_command(self, args, original_input):
        """Вывод содержимого файла (Этап 4)"""
        if len(args) < 1:
            print("cat: требуется как минимум 1 аргумент")
            print("Использование: cat файл1 [файл2 ...]")
            return False

        success = True
        for filename in args:
            file_path = self._normalize_path(filename)

            if file_path not in self.filesystem:
                print(f"cat: {filename}: Нет такого файла")
                success = False
                continue

            if self.filesystem[file_path]["type"] != "file":
                print(f"cat: {filename}: Не является файлом")
                success = False
                continue

            content = self.filesystem[file_path].get("content", "")
            print(f"=== {filename} ===")
            print(content)
            if content and not content.endswith('\n'):
                print()

        return success

    def find_command(self, args, original_input):
        """Поиск файлов (Этап 4)"""
        if len(args) < 1:
            print("find: требуется как минимум 1 аргумент")
            print("Использование: find имя [путь]")
            return False

        name = args[0]
        start_path = self.current_path

        if len(args) > 1:
            start_path = self._normalize_path(args[1])

        if start_path not in self.filesystem or self.filesystem[start_path]["type"] != "dir":
            print(f"find: {start_path}: Нет такой директории")
            return False

        found = []
        for path in self.filesystem:
            if path.startswith(start_path):
                item_name = path.split("/")[-1]
                if name in item_name:  # Простой поиск по подстроке
                    found.append(path)

        print(f"Поиск '{name}' в {start_path}:")
        if found:
            for path in found:
                item_type = "dir" if self.filesystem[path]["type"] == "dir" else "file"
                print(f"  {path} ({item_type})")
        else:
            print("  Не найдено")

        return True

    def tac_command(self, args, original_input):
        """Обратный вывод файла (Этап 4)"""
        if len(args) < 1:
            print("tac: требуется как минимум 1 аргумент")
            print("Использование: tac файл1 [файл2 ...]")
            return False

        success = True
        for filename in args:
            file_path = self._normalize_path(filename)

            if file_path not in self.filesystem:
                print(f"tac: {filename}: Нет такого файла")
                success = False
                continue

            if self.filesystem[file_path]["type"] != "file":
                print(f"tac: {filename}: Не является файлом")
                success = False
                continue

            content = self.filesystem[file_path].get("content", "")
            lines = content.split("\n")

            print(f"=== {filename} (обратный порядок) ===")
            for line in reversed(lines):
                print(line)
            if lines and lines[-1]:
                print()

        return success

    def conf_dump_command(self, args, original_input):
        if len(args) > 0:
            print("conf-dump: слишком много аргументов")
            return False

        print("=== Конфигурация VFS ===")
        print(f"Имя VFS: {self.vfs_name}")
        print(f"Текущий путь: {self.current_path}")
        print(f"VFS путь: {self.vfs_path}")
        print(f"Стартовый скрипт: {self.startup_script}")
        print(f"Размер файловой системы: {len(self.filesystem)} объектов")
        print("========================")
        return True

    def list_scripts_command(self, args, original_input):
        if len(args) > 0:
            print("list-scripts: слишком много аргументов")
            return False

        print("Доступные скрипты (*.txt):")
        print("-" * 40)

        scripts = [f for f in os.listdir('.') if f.endswith('.txt')]
        if scripts:
            for i, script in enumerate(scripts, 1):
                print(f"  {i}. {script}")
        else:
            print("  Скрипты не найдены")
            print("  Создайте .txt файлы с командами в этой папке")

        print("-" * 40)
        return True

    def run_script_command(self, args, original_input):
        if len(args) != 1:
            print("run-script: требуется ровно 1 аргумент - имя скрипта")
            print("Использование: run-script имя_файла.txt")
            print("Используйте 'list-scripts' чтобы увидеть доступные скрипты")
            return False

        script_file = args[0]
        if not script_file.endswith('.txt'):
            script_file += '.txt'

        return self.execute_script_file(script_file)

    def execute_script_file(self, script_file):
        if not os.path.exists(script_file):
            print(f"Ошибка: скрипт '{script_file}' не найден")
            print("Используйте 'list-scripts' чтобы увидеть доступные скрипты")
            return False

        print(f"Выполнение скрипта: {script_file}")
        print("=" * 50)

        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            success_count = 0
            error_count = 0

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                if not line:
                    continue
                if line.startswith('#'):
                    print(f"# {line[1:].strip()}")
                    continue

                print(f"[Строка {line_num}] {self.vfs_name}:{self.current_path}$ {line}")

                command, args = self.parse_input(line)

                if command:
                    success = self.execute_command(command, args, line)
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        print(f"ОШИБКА в строке {line_num}")
                else:
                    error_count += 1
                    print(f"ОШИБКА: Не удалось разобрать команду в строке {line_num}")

                print()

            print("=" * 50)
            print(f"Скрипт '{script_file}' выполнен:")
            print(f"  Успешных команд: {success_count}")
            print(f"  Ошибочных команд: {error_count}")

            return error_count == 0

        except Exception as e:
            print(f"Критическая ошибка выполнения скрипта: {e}")
            return False

    def pwd_command(self, args, original_input):
        if len(args) > 0:
            print("pwd: слишком много аргументов")
            return False

        print(self.current_path)
        return True

    def mkdir_command(self, args, original_input):
        if len(args) != 1:
            print("mkdir: требуется ровно 1 аргумент - имя директории")
            return False

        dir_name = args[0]
        new_path = f"{self.current_path}/{dir_name}" if self.current_path != "/" else f"/{dir_name}"

        if new_path in self.filesystem:
            print(f"mkdir: невозможно создать директорию '{dir_name}': Файл существует")
            return False

        self.filesystem[new_path] = {"type": "dir", "children": []}

        parent = self.current_path if self.current_path != "/" else "/"
        if parent in self.filesystem:
            self.filesystem[parent]["children"].append(dir_name)

        print(f"Директория '{dir_name}' создана")
        return True

    def touch_command(self, args, original_input):
        if len(args) != 1:
            print("touch: требуется ровно 1 аргумент - имя файла")
            return False

        file_name = args[0]
        file_path = f"{self.current_path}/{file_name}" if self.current_path != "/" else f"/{file_name}"

        if file_path in self.filesystem:
            print(f"Файл '{file_name}' уже существует")
            return True

        self.filesystem[file_path] = {"type": "file", "content": ""}

        parent = self.current_path if self.current_path != "/" else "/"
        if parent in self.filesystem:
            self.filesystem[parent]["children"].append(file_name)

        print(f"Файл '{file_name}' создан")
        return True

    def history_command(self, args, original_input):
        if len(args) > 0:
            print("history: слишком много аргументов")
            return False

        print("История команд:")
        print("-" * 40)
        for i, cmd in enumerate(self.command_history[-10:], 1):
            print(f"  {i:2d}. {cmd}")
        print("-" * 40)
        return True

    def execute_startup_script(self):
        if not self.startup_script:
            return True

        if not self.startup_script.endswith('.txt'):
            self.startup_script += '.txt'

        if not os.path.exists(self.startup_script):
            print(f"Ошибка: стартовый скрипт '{self.startup_script}' не найден")
            return False

        print(f"Запуск стартового скрипта: {self.startup_script}")
        return self.execute_script_file(self.startup_script)

    def run(self):
        if self.startup_script:
            if not self.execute_startup_script():
                print("Не удалось выполнить стартовый скрипт")
                return

        print("Эмулятор VFS запущен")
        print(
            "Доступные команды: ls, cd, pwd, mkdir, touch, history, conf-dump, run-script, list-scripts, cat, find, tac, exit")
        print("Используйте 'list-scripts' чтобы увидеть доступные .txt скрипты")
        print("Используйте 'run-script имя_файла' для запуска скрипта")
        print("=" * 60)

        while self.running:
            try:
                self.print_prompt()
                user_input = input().strip()

                if not user_input:
                    continue

                command, args = self.parse_input(user_input)
                if command:
                    self.execute_command(command, args, user_input)
                    print()

            except (EOFError, KeyboardInterrupt):
                print("\nВыход из эмулятора VFS...")
                break
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Эмулятор VFS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  python vfs_emulator.py                                    # Интерактивный режим
  python vfs_emulator.py --list-scripts                    # Показать скрипты
  python vfs_emulator.py --run-script test.txt             # Выполнить скрипт
  python vfs_emulator.py --startup-script auto.txt         # Автозапуск скрипта
  python vfs_emulator.py --vfs-path ./test_vfs --run-script setup.txt
        '''
    )

    parser.add_argument('--vfs-path', help='Путь к VFS (директория для загрузки)')
    parser.add_argument('--startup-script', help='Стартовый скрипт (txt файл)')
    parser.add_argument('--run-script', help='Запустить конкретный скрипт и выйти')
    parser.add_argument('--list-scripts', action='store_true',
                        help='Показать доступные скрипты и выйти')

    args = parser.parse_args()

    if args.list_scripts:
        scripts = [f for f in os.listdir('.') if f.endswith('.txt')]
        print("Доступные скрипты (*.txt) в текущей директории:")
        print("=" * 50)
        if scripts:
            for script in scripts:
                print(f"  {script}")
            print(f"\nВсего скриптов: {len(scripts)}")
        else:
            print("  Скрипты не найдены")
            print("  Создайте .txt файлы с командами в этой папке")
        print("=" * 50)
        return

    if args.run_script:
        emulator = VFSEmulator(vfs_path=args.vfs_path)
        success = emulator.execute_script_file(args.run_script)
        sys.exit(0 if success else 1)

    emulator = VFSEmulator(
        vfs_path=args.vfs_path,
        startup_script=args.startup_script
    )
    emulator.run()


if __name__ == "__main__":
    main()