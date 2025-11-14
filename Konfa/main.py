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

        print("=== Параметры запуска ===")
        print(f"vfs_path: {self.vfs_path}")
        print(f"startup_script: {self.startup_script}")
        print("========================")
        print()

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
        else:
            print(f"{command}: команда не найдена")
            return False

    def exit_command(self, args, original_input):
        # Правильная проверка аргументов
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

    def ls_command(self, args, original_input):
        # Правильная проверка аргументов
        if len(args) > 0:
            print("ls: слишком много аргументов")
            return False

        print(f"Содержимое директории {self.current_path}:")
        print("  file1.txt")
        print("  file2.txt")
        print("  directory/")
        return True

    def cd_command(self, args, original_input):
        # Правильная проверка аргументов
        if len(args) > 1:
            print("cd: слишком много аргументов")
            return False

        new_path = args[0] if args else "/"

        # Простая эмуляция смены директории
        if new_path == "/":
            self.current_path = "/"
        elif new_path == "..":
            if self.current_path != "/":
                self.current_path = "/"
        else:
            if self.current_path == "/":
                self.current_path = f"/{new_path}"
            else:
                self.current_path = f"{self.current_path}/{new_path}"

        print(f"Переход в директорию: {self.current_path}")
        return True

    def conf_dump_command(self, args, original_input):
        # Правильная проверка аргументов
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
        # Правильная проверка аргументов
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
        # ПРАВИЛЬНАЯ проверка аргументов
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
        # Запускаем стартовый скрипт если указан
        if self.startup_script:
            if not self.execute_startup_script():
                print("Не удалось выполнить стартовый скрипт")
                return

        print("Эмулятор VFS запущен")
        print("Доступные команды: ls, cd, conf-dump, run-script, list-scripts, exit")
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
    parser = argparse.ArgumentParser(description='Эмулятор VFS',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog='''
Примеры использования:
  python vfs_emulator.py                                    # Интерактивный режим
  python vfs_emulator.py --list-scripts                    # Показать скрипты
  python vfs_emulator.py --run-script test.txt             # Выполнить скрипт
  python vfs_emulator.py --startup-script auto.txt         # Автозапуск скрипта
  python vfs_emulator.py --vfs-path /my/vfs --run-script setup.txt
                                   ''')

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