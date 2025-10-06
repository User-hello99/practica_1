@echo off
echo === Тестирование минимальной VFS ===

REM Создаем минимальную VFS с одним файлом
echo /,readme.txt,"Добро пожаловать в минимальную VFS!",root > minimal_vfs.csv

REM Запускаем эмулятор с минимальной VFS
python emulator.py --vfs minimal_vfs.csv

REM Очистка
del minimal_vfs.csv

pause