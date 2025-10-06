@echo off
echo === more ===

REM Создаем тестовую VFS
(
echo /,readme.txt,"fgf",root
echo /home,users.txt,"dfdfdf",admin
echo /home/user1,file1.txt,"Файл пользователя 1",user1
echo /home/user1,file2.txt,"Второй файл user1",user1
echo /home/user2,document.doc,"Документ user2",user2
echo /var,log.txt,"Системные логи",root
) > test_vfs.csv

REM Создаем скрипт для выполнения в эмуляторе
(
echo # Тестовый скрипт для эмулятора VFS
echo echo "=== Начало тестирования ==="
echo pwd
echo ls
echo ls -l /home/user1/file1.txt
echo cd home
echo ls
echo cd user1
echo pwd
echo ls
echo cat file1.txt
echo cd ..
echo cd user2
echo cat document.doc
echo cd ../..
echo du
echo chown newuser /home/user1/file1.txt
echo ls -l /home/user1/file1.txt
echo echo "=== Тестирование завершено ==="
) > test_script.txt

REM Запускаем эмулятор с VFS и скриптом
python emulator.py --vfs test_vfs.csv --script test_script.txt

REM Очистка
del test_vfs.csv
del test_script.txt

pause