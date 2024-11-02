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

echo "Зупиняємо Docker..."

# Зупиняємо та видаляємо всі контейнери, ім'я яких починається на elixir_
containers=$(sudo docker ps -a --filter "name=^elixir_" --format "{{.ID}}")
if [ -n "$containers" ]; then
    sudo docker stop $containers
    sudo docker rm $containers
fi

# Зупиняємо старі контейнери з ім'ям elixir
old_containers=$(sudo docker ps -a --filter "name=elixir" --format "{{.ID}}")
if [ -n "$old_containers" ]; then
    sudo docker stop $old_containers
    sudo docker rm $old_containers
    containers=("${old_containers[@]}" "${containers[@]}")

    # Перейменовуємо файл validator.env на validator_1.env
    echo "Перейменовуємо файл validator.env на validator_1.env..."
    mv ~/elxnode/validator.env ~/elxnode/validator_1.env
fi

# Видаляємо старі образи
echo "Видаляємо старі образи..."
old_images=$(sudo docker images --filter "reference=elixirprotocol/validator" --format "{{.ID}}")
if [ -n "$old_images" ]; then
    sudo docker rmi $old_images -f
fi
echo "Видалення старих образів завершено."

# Завантажуємо новий образ Docker для Elixir validator
echo "Завантажуємо новий образ Docker для Elixir validator..."
docker pull elixirprotocol/validator --platform linux/amd64

# Запускаємо нові контейнери з унікальними портами
echo "Запускаємо нові контейнери Docker..."
i=1
for container in $containers; do
    env_file=~/elxnode/validator_$i.env
    CONTAINER_PORT=$((START_PORT + i - 1))
    # Перевіряємо та додаємо параметр ENV=prod до кожного файлу validator_*.env
    if ! grep -q '^ENV=prod' "$env_file"; then
        echo "Додаємо ENV=prod до $env_file"
        sed -i 's/^ENV=.*/ENV=prod/' "$env_file"
    fi
    docker run -d \
    -p $CONTAINER_PORT:$START_PORT \
    --env-file $env_file \
    --name elixir_$i \
    --restart unless-stopped \
    elixirprotocol/validator
    i=$((i + 1))
done

echo "Скрипт завершено. Контейнери Elixir оновлено та запущено на портах, починаючи з $START_PORT."
