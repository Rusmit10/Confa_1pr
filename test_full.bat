@echo off
echo === ЗАПУСК VFS ЭМУЛЯТОРА ===
echo.

REM 1. Запуск как в вашем примере
echo 1. Запуск эмулятора (полный путь):
start /wait "" "C:\Users\aser\AppData\Local\Programs\Python\Python311\python.exe" "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\main.py"
echo.

REM 2. Создаем папку для теста
echo 2. Создаем тестовую папку...
mkdir "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_data" 2>nul
echo Тестовый файл > "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_data\file1.txt"
echo Еще один файл > "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_data\file2.txt"

REM 3. Запуск с VFS путем
echo.
echo 3. Запуск с загрузкой VFS:
start /wait "" "C:\Users\aser\AppData\Local\Programs\Python\Python311\python.exe" "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\main.py" --vfs-path "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_data"
echo.

REM 4. Создаем тестовый скрипт
echo 4. Создаем тестовый скрипт...
echo pwd > "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_script.txt"
echo ls -l >> "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_script.txt"
echo cat file1.txt >> "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_script.txt"
echo exit >> "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_script.txt"

REM 5. Запуск со скриптом
echo.
echo 5. Запуск со скриптом:
start /wait "" "C:\Users\aser\AppData\Local\Programs\Python\Python311\python.exe" "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\main.py" --run-script "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_script.txt"
echo.

REM 6. Запуск с параметрами
echo 6. Запуск с параметрами:
start /wait "" "C:\Users\aser\AppData\Local\Programs\Python\Python311\python.exe" "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\main.py" --list-scripts
echo.

REM 7. Очистка
echo 7. Очистка...
del "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_script.txt" 2>nul
rd /s /q "C:\Users\aser\PycharmProjects\Confa_1pr\konfa\test_data" 2>nul

echo.
echo === ТЕСТ ЗАВЕРШЕН ===
pause