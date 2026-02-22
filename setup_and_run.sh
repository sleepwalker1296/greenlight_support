#!/bin/bash
# Установка зависимостей и запуск бота через screen с автоперезапуском

set -e
cd "$(dirname "$0")"

echo "=== Установка зависимостей ==="
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt

echo "=== Остановка старой сессии (если есть) ==="
screen -S greenlight_bot -X quit 2>/dev/null || true

echo "=== Запуск бота в screen ==="
screen -dmS greenlight_bot bash -c '
  while true; do
    echo "[$(date)] Запуск бота..."
    python3 run.py
    echo "[$(date)] Бот упал, перезапуск через 5 сек..."
    sleep 5
  done
'

echo "=== Бот запущен ==="
echo "Логи: screen -r greenlight_bot"
echo "Остановить: screen -S greenlight_bot -X quit"
