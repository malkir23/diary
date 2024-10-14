#!/bin/bash

# Запитуємо стартовий порт
read -p "Введіть стартовий порт для першого контейнера: " START_PORT

# Перевірка наявності Docker
if ! [ -x "$(command -v docker)" ]; then
    echo "Docker не встановлений. Встановлюємо Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
else
    echo "Docker вже встановлений."
fi

echo "Зупиняюмо Docker..."

# Зупиняємо та видаляємо всі контейнери, ім'я яких починається на elixir_
containers=$(sudo docker ps -a --filter "name=^elixir_" --format "{{.ID}}")
if [ -n "$containers" ]; then
    sudo docker stop $containers
    sudo docker rm $containers
fi

# Зупиняємо всі контейнери старі
old_containers=$(sudo docker ps -a --filter "name=elixir" --format "{{.ID}}")
if [ -n "$old_containers" ]; then
    sudo docker stop $old_containers
    sudo docker rm $old_containers
    containers=("${old_containers[@]}" "${containers[@]}")
    # Перейменовуємо файл validator.env на validator_1.env
    if [ -f "~/elxnode/validator.env" ]; then
        echo "Перейменовуємо файл validator.env на validator_1.env..."
        mv ~/elxnode/validator.env ~/elxnode/validator_1.env
    fi
fi

#Видаляємо старі образи
echo "Видаляємо старі образи..."
old_images=$(sudo docker images --filter "reference=elixirprotocol/validator" --format "{{.ID}}")
if [ -n "$old_images" ]; then
    sudo docker rmi $old_images -f
fi
echo "Видаляємо старі образи завершено."

echo "Завантажуємо образ Docker для Elixir validator..."
docker pull elixirprotocol/validator:v3 --platform linux/amd64

echo "Запускаємо Docker для всіх зупинених контейнерів..."
i=1
for container in $containers; do
    CONTAINER_PORT=$((START_PORT + i - 1))
    docker run -d \
    -p $CONTAINER_PORT:$START_PORT \
    --env-file ~/elxnode/validator_$i.env \
    --name elixir_$i \
    --restart unless-stopped \
    elixirprotocol/validator:v3
    i=$((i + 1))
done

echo "Скрипт завершено. Контейнер Elixir оновленно."
