#!/bin/bash

# Перевірка наявності Docker
if ! [ -x "$(command -v docker)" ]; then
    echo "Docker не встановлений. Встановлюємо Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
else
    echo "Docker вже встановлений."
fi

echo "Зупиняюмо Docker..."
sudo docker stop elixir
sudo docker kill elixir
sudo docker rm elixir

echo "Завантажуємо образ Docker для Elixir validator..."
docker pull elixirprotocol/validator:v3 --platform linux/amd64

echo "Запускаємо Docker..."
docker run -d \
--env-file /root/elxnode/validator.env \
--name elixir \
--restart unless-stopped \
--platform linux/amd64 -p 17690:17690 \
elixirprotocol/validator:v3


echo "Скрипт завершено. Контейнер Elixir оновленно."
