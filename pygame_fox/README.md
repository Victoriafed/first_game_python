### pygame_fox

Первая игра разработанная с помощью библиотеки pygame. 


Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```
 
Запуск игры:

```
python My_game_fox.py
```

Запуск редактора уровней:
```
python fox_level_editor.py
```

Перезагрузка файла .exe:
```
pyinstaller --onefile --icon="C:\Dev\game\pygame_start\pygame_fox\images\icon.ico" --noconsole My_game_fox.py
```