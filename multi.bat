@echo off
echo === files ===

REM Создаем VFS с несколькими файлами в корне
(
echo /,file1.txt,"hello",user1
echo /,file2.txt,"hello2",user2
echo /,document.doc,"hedsfsdf",user1
echo /,config.ini,"config_value=123",root
echo /,backup.bak,"fddsfsd",user3
) > multiple_files_vfs.csv

REM Запускаем эмулятор
python emulator.py --vfs multiple_files_vfs.csv

REM Очистка
del multiple_files_vfs.csv

pause