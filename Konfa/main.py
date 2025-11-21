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
        self.command_history = []  # История команд для реализации history
        # Виртуальная файловая система с начальной структурой
        self.filesystem = {
            "/": {"type": "dir", "children": ["home", "etc", "var"]},
            "/home": {"type": "dir", "children": ["user1", "user2"]},
            "/etc": {"type": "dir", "children": ["config.txt"]},
            "/var": {"type": "dir", "children": ["log"]},
            "/home/user1": {"type": "dir", "children": ["documents"]},
            "/home/user2": {"type": "dir", "children": ["downloads"]},
        }

        # Отладочный вывод параметров запуска
        print("=== Параметры запуска ===")
        print(f"vfs_path: {self.vfs_path}")
        print(f"startup_script: {self.startup_script}")
        print("========================")
        print()

    def print_prompt(self):
        """Вывод приглашения командной строки"""
        print(f"{self.vfs_name}:{self.current_path}$ ", end="", flush=True)

    def parse_input(self, user_input):
        """Парсинг ввода пользователя на команду и аргументы"""
        try:
            parts = shlex.split(user_input.strip())
            if not parts:
                return None, []
            return parts[0], parts[1:]
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            return None, []

    def execute_command(self, command, args, original_input):
        """Главный диспетчер команд"""
        # Добавляем команду в историю
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
        else:
            print(f"{command}: команда не найдена")
            return False

    def exit_command(self, args, original_input):
        """Команда выхода из эмулятора"""
        if len(args) > 1:
            print("exit: слишком много аргументов")
            return False

        if len(args) == 1:
            try:
                int(args[0])  # Проверяем что код выхода - число
            except ValueError:
                print("exit: неверный код выхода")
                return False

        self.running = False
        print("Выход из эмулятора VFS")
        return True

    def ls_command(self, args, original_input):
        """Команда списка файлов с поддержкой путей и -l"""
        # Обработка аргументов
        long_format = False
        target_path = self.current_path

        if args:
            # Проверяем формат вывода
            if "-l" in args:
                long_format = True
                args = [arg for arg in args if arg != "-l"]

            # Обрабатываем путь если указан
            if args:
                if len(args) > 1:
                    print("ls: слишком много аргументов")
                    return False
                target_path = args[0]

        # Нормализуем путь
        if target_path != self.current_path:
            if target_path.startswith("/"):
                # Абсолютный путь
                normalized_path = target_path
            else:
                # Относительный путь
                if self.current_path == "/":
                    normalized_path = f"/{target_path}"
                else:
                    normalized_path = f"{self.current_path}/{target_path}"
        else:
            normalized_path = self.current_path if self.current_path != "/" else "/"

        # Проверяем существование директории
        if normalized_path not in self.filesystem or self.filesystem[normalized_path]["type"] != "dir":
            print(f"ls: невозможно получить доступ к '{target_path}': Нет такой директории")
            return False

        children = self.filesystem[normalized_path]["children"]

        print(f"Содержимое директории {target_path}:")

        # Вывод в коротком или длинном формате
        for item in children:
            item_path = f"{normalized_path}/{item}" if normalized_path != "/" else f"/{item}"
            if item_path not in self.filesystem:
                continue

            if long_format:
                # Длинный формат с правами доступа
                item_type = "d" if self.filesystem[item_path]["type"] == "dir" else "-"
                print(f"{item_type}rw-r--r-- 1 user user    0 Nov 15 12:00 {item}")
            else:
                # Короткий формат
                item_suffix = "/" if self.filesystem[item_path]["type"] == "dir" else ""
                print(f"  {item}{item_suffix}")
        return True

    def cd_command(self, args, original_input):
        """Команда смены директории"""
        if len(args) > 1:
            print("cd: слишком много аргументов")
            return False

        new_path = args[0] if args else "/"
        target_path = ""

        # Логика определения целевого пути
        if new_path == "/":
            target_path = "/"
        elif new_path == "..":
            # Поддержка перехода на уровень выше
            if self.current_path == "/":
                target_path = "/"
            else:
                parts = self.current_path.split("/")
                target_path = "/" + "/".join(parts[1:-1]) if len(parts) > 2 else "/"
        else:
            # Относительный путь
            if self.current_path == "/":
                target_path = f"/{new_path}"
            else:
                target_path = f"{self.current_path}/{new_path}"

        # Проверка существования директории
        if target_path not in self.filesystem or self.filesystem[target_path]["type"] != "dir":
            print(f"cd: {new_path}: Нет такой директории")
            return False

        self.current_path = target_path
        print(f"Переход в директорию: {self.current_path}")
        return True

    def conf_dump_command(self, args, original_input):
        """Команда вывода конфигурации"""
        if len(args) > 0:
            print("conf-dump: слишком много аргументов")
            return False

        print("=== Конфигурация VFS ===")
        print(f"Имя VFS: {self.vfs_name}")
        print(f"Текущий путь: {self.current_path}")
        print(f"VFS путь: {self.vfs_path}")
        print(f"Стартовый скрипт: {self.startup_script}")
        return True

    def list_scripts_command(self, args, original_input):
        """Показать доступные скрипты"""
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
        """Выполнение скрипта из txt файла"""
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
        """Выполнение команд из txt файла"""
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

                # Пропускаем пустые строки и комментарии
                if not line:
                    continue
                if line.startswith('#'):
                    print(f"# {line[1:].strip()}")
                    continue

                # Выводим команду
                print(f"[Строка {line_num}] {self.vfs_name}:{self.current_path}$ {line}")

                # Выполняем команду
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
        """Команда показа текущей директории"""
        if len(args) > 0:
            print("pwd: слишком много аргументов")
            return False

        print(self.current_path)
        return True

    def mkdir_command(self, args, original_input):
        """Команда создания директории"""
        if len(args) != 1:
            print("mkdir: требуется ровно 1 аргумент - имя директории")
            return False

        dir_name = args[0]
        new_path = f"{self.current_path}/{dir_name}" if self.current_path != "/" else f"/{dir_name}"

        if new_path in self.filesystem:
            print(f"mkdir: невозможно создать директорию '{dir_name}': Файл существует")
            return False

        # Создаем новую директорию
        self.filesystem[new_path] = {"type": "dir", "children": []}

        # Добавляем в родительскую директорию
        parent = self.current_path if self.current_path != "/" else "/"
        if parent in self.filesystem:
            self.filesystem[parent]["children"].append(dir_name)

        print(f"Директория '{dir_name}' создана")
        return True

    def touch_command(self, args, original_input):
        """Команда создания файла"""
        if len(args) != 1:
            print("touch: требуется ровно 1 аргумент - имя файла")
            return False

        file_name = args[0]
        file_path = f"{self.current_path}/{file_name}" if self.current_path != "/" else f"/{file_name}"

        if file_path in self.filesystem:
            print(f"Файл '{file_name}' уже существует")
            return True  # touch может просто обновить время, но у нас это успех

        # Создаем новый файл
        self.filesystem[file_path] = {"type": "file", "content": ""}

        # Добавляем в текущую директорию
        parent = self.current_path if self.current_path != "/" else "/"
        if parent in self.filesystem:
            self.filesystem[parent]["children"].append(file_name)

        print(f"Файл '{file_name}' создан")
        return True

    def history_command(self, args, original_input):
        """Команда показа истории команд"""
        if len(args) > 0:
            print("history: слишком много аргументов")
            return False

        print("История команд:")
        print("-" * 40)
        # Показываем последние 10 команд
        for i, cmd in enumerate(self.command_history[-10:], 1):
            print(f"  {i:2d}. {cmd}")
        print("-" * 40)
        return True

    def execute_startup_script(self):
        """Выполнение стартового скрипта"""
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
        """Главный цикл выполнения эмулятора"""
        # Запускаем стартовый скрипт если указан
        if self.startup_script:
            if not self.execute_startup_script():
                print("Не удалось выполнить стартовый скрипт")
                return

        print("Эмулятор VFS запущен")
        print("Доступные команды: ls, cd, pwd, mkdir, touch, history, conf-dump, run-script, list-scripts, exit")
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
    """Главная функция с парсингом аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Эмулятор VFS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  python vfs_emulator.py                                    # Интерактивный режим
  python vfs_emulator.py --list-scripts                    # Показать скрипты
  python vfs_emulator.py --run-script test.txt             # Выполнить скрипт
  python vfs_emulator.py --startup-script auto.txt         # Автозапуск скрипта
  python vfs_emulator.py --vfs-path /my/vfs --run-script setup.txt
        '''
    )

    parser.add_argument('--vfs-path', help='Путь к VFS')
    parser.add_argument('--startup-script', help='Стартовый скрипт (txt файл)')
    parser.add_argument('--run-script', help='Запустить конкретный скрипт и выйти')
    parser.add_argument('--list-scripts', action='store_true',
                        help='Показать доступные скрипты и выйти')

    args = parser.parse_args()

    # Режим показа скриптов
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

    # Режим выполнения одного скрипта
    if args.run_script:
        emulator = VFSEmulator(vfs_path=args.vfs_path)
        success = emulator.execute_script_file(args.run_script)
        sys.exit(0 if success else 1)

    # Интерактивный режим
    emulator = VFSEmulator(
        vfs_path=args.vfs_path,
        startup_script=args.startup_script
    )
    emulator.run()


if __name__ == "__main__":
    main()