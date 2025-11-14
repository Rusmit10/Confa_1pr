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
        original_parts = original_input.strip().split()
        if len(original_parts) > 2:
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
        original_parts = original_input.strip().split()
        if len(original_parts) > 1:
            print("ls: слишком много аргументов")
            return False

        print(f"ls с аргументами: {args}")
        return True

    def cd_command(self, args, original_input):
        original_parts = original_input.strip().split()
        if len(original_parts) > 2:
            print("cd: слишком много аргументов")
            return False

        new_path = args[0] if args else "/"
        print(f"cd в директорию: {new_path}")
        self.current_path = new_path
        return True

    def conf_dump_command(self, args, original_input):
        original_parts = original_input.strip().split()
        if len(original_parts) > 1:
            print("conf-dump: слишком много аргументов")
            return False

        print("Конфигурация:")
        print(f"  vfs_path: {self.vfs_path}")
        print(f"  startup_script: {self.startup_script}")
        print(f"  current_path: {self.current_path}")
        return True

    def list_scripts_command(self, args, original_input):
        """Показать доступные скрипты"""
        original_parts = original_input.strip().split()
        if len(original_parts) > 1:
            print("list-scripts: слишком много аргументов")
            return False

        print("Доступные скрипты (*.txt):")
        print("-" * 30)

        scripts = [f for f in os.listdir('.') if f.endswith('.txt')]
        if scripts:
            for script in scripts:
                print(f"  {script}")
        else:
            print("  Скрипты не найдены")
            print("  Создайте .txt файлы с командами в этой папке")

        print("-" * 30)
        return True

    def run_script_command(self, args, original_input):
        """Выполнение скрипта из txt файла"""
        original_parts = original_input.strip().split()
        if len(original_parts) > 2:
            print("run-script: слишком много аргументов")
            return False

        if len(args) == 0:
            print("run-script: укажите имя скрипта")
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
        print("-" * 40)

        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    print(f"{self.vfs_name}:{self.current_path}$ {line}")
                    command, args = self.parse_input(line)

                    if command:
                        if not self.execute_command(command, args, line):
                            print(f"Ошибка в строке {line_num}")
                            return False
                    print()

            print("-" * 40)
            print(f"Скрипт '{script_file}' выполнен успешно")
            return True

        except Exception as e:
            print(f"Ошибка выполнения скрипта: {e}")
            return False

    def execute_startup_script(self):
        if not self.startup_script:
            return True

        if not self.startup_script.endswith('.txt'):
            self.startup_script += '.txt'

        if not os.path.exists(self.startup_script):
            print(f"Ошибка: стартовый скрипт '{self.startup_script}' не найден")
            return False

        return self.execute_script_file(self.startup_script)

    def run(self):
        if self.startup_script and not self.execute_startup_script():
            return

        print("Эмулятор VFS. Команды: ls, cd, conf-dump, run-script, list-scripts, exit")
        print("Используйте 'list-scripts' чтобы увидеть доступные .txt скрипты")
        print("Используйте 'run-script имя_файла' для запуска скрипта")
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


def main():
    parser = argparse.ArgumentParser(description='Эмулятор VFS')
    parser.add_argument('--vfs-path', help='Путь к VFS')
    parser.add_argument('--startup-script', help='Стартовый скрипт (txt файл)')
    parser.add_argument('--run-script', help='Запустить конкретный скрипт')
    parser.add_argument('--list-scripts', action='store_true',
                        help='Показать доступные скрипты')

    args = parser.parse_args()

    if args.list_scripts:
        scripts = [f for f in os.listdir('.') if f.endswith('.txt')]
        print("Доступные скрипты (*.txt):")
        print("-" * 30)
        if scripts:
            for script in scripts:
                print(f"  {script}")
        else:
            print("  Скрипты не найдены")
            print("  Создайте .txt файлы с командами в этой папке")
        return

    if args.run_script:
        emulator = VFSEmulator(vfs_path=args.vfs_path)
        emulator.execute_script_file(args.run_script)
        return

    emulator = VFSEmulator(
        vfs_path=args.vfs_path,
        startup_script=args.startup_script
    )
    emulator.run()


if __name__ == "__main__":
    main()