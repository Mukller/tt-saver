#!/bin/bash

# Переходим в папку проекта
cd /home/anton/Tiktok-saver

# Активируем виртуальное окружение
source venv/bin/activate

# Запуск бота
exec python3 app.py
