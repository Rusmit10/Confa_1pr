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
        else:
            print(f"{command}: команда не найдена")
            return False

    def exit_command(self, args, original_input):
        # Проверяем количество аргументов в исходной строке
        original_parts = original_input.strip().split()
        if len(original_parts) > 2:  # команда + максимум 1 аргумент
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
        # Проверяем количество аргументов в исходной строке
        original_parts = original_input.strip().split()
        if len(original_parts) > 1:  # только команда, без аргументов
            print("ls: слишком много аргументов")
            return False

        print(f"ls с аргументами: {args}")
        return True

    def cd_command(self, args, original_input):
        # Проверяем количество аргументов в исходной строке
        original_parts = original_input.strip().split()
        if len(original_parts) > 2:  # команда + максимум 1 аргумент
            print("cd: слишком много аргументов")
            return False

        new_path = args[0] if args else "/"
        print(f"cd в директорию: {new_path}")
        self.current_path = new_path
        return True

    def conf_dump_command(self, args, original_input):
        # Проверяем количество аргументов в исходной строке
        original_parts = original_input.strip().split()
        if len(original_parts) > 1:  # только команда, без аргументов
            print("conf-dump: слишком много аргументов")
            return False

        print("Конфигурация:")
        print(f"  vfs_path: {self.vfs_path}")
        print(f"  startup_script: {self.startup_script}")
        print(f"  current_path: {self.current_path}")
        return True

    def execute_startup_script(self):
        if not self.startup_script:
            return True

        if not os.path.exists(self.startup_script):
            print(f"Ошибка: скрипт '{self.startup_script}' не найден")
            return False

        print(f"Выполнение скрипта: {self.startup_script}")
        print("-" * 40)

        try:
            with open(self.startup_script, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    print(f"{self.vfs_name}:{self.current_path}$ {line}")
                    command, args = self.parse_input(line)

                    if command and not self.execute_command(command, args, line):
                        print(f"Ошибка в строке {line_num}")
                        return False
                    print()

            print("-" * 40)
            return True

        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def run(self):
        if self.startup_script and not self.execute_startup_script():
            return

        print("Эмулятор VFS. Команды: ls, cd, conf-dump, exit")
        print("-" * 40)

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
                print("\nВыход...")
                break
            except Exception as e:
                print(f"Ошибка: {e}")


def create_test_scripts():
    """Создает 3 коротких тестовых скрипта"""
    scripts = {
        'test1.vfs': '''# Простой тест
ls
cd /home
conf-dump
ls -la''',

        'test2.vfs': '''# Тест с ошибкой
ls
cd too many args
ls "arg1 arg2"''',

        'test3.vfs': '''# Тест conf-dump
conf-dump
cd /tmp
conf-dump
exit'''
    }

    for filename, content in scripts.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"Создан: {filename}")


def run_quick_demo():
    """Быстрая демонстрация"""
    print("=== БЫСТРАЯ ДЕМОНСТРАЦИЯ ===")

    # Создаем скрипты
    create_test_scripts()

    # Тест 1
    print("\n1. Тест со скриптом:")
    emulator = VFSEmulator(vfs_path="/demo", startup_script="test1.vfs")
    emulator.run()

    # Тест 2
    print("\n2. Тест с ошибкой:")
    emulator = VFSEmulator(startup_script="test2.vfs")
    emulator.run()

    # Тест 3
    print("\n3. Интерактивный режим:")
    emulator = VFSEmulator(vfs_path="/final")
    emulator.run()


def main():
    parser = argparse.ArgumentParser(description='Эмулятор VFS')
    parser.add_argument('--vfs-path', help='Путь к VFS')
    parser.add_argument('--startup-script', help='Стартовый скрипт')
    parser.add_argument('--create-scripts', action='store_true',
                        help='Создать тестовые скрипты')
    parser.add_argument('--demo', action='store_true',
                        help='Запустить демонстрацию')

    args = parser.parse_args()

    if args.create_scripts:
        create_test_scripts()
        return

    if args.demo:
        run_quick_demo()
        return

    emulator = VFSEmulator(
        vfs_path=args.vfs_path,
        startup_script=args.startup_script
    )
    emulator.run()


if __name__ == "__main__":
    main()