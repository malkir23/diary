#!/bin/bash

# Створюємо папку elxnode в корені
mkdir -p /root/elxnode

# Запитуємо кількість Docker копій у користувача
read -p "Введіть кількість Docker копій (контейнерів): " CONTAINER_COUNT

# Запитуємо стартовий порт
read -p "Введіть стартовий порт для першого контейнера: " START_PORT

# Встановлюємо Docker (якщо ще не встановлено)
if ! command -v docker &> /dev/null
then
    echo "Docker не встановлений. Встановлюємо Docker..."

    # Додаємо офіційний ключ Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Додаємо репозиторій Docker
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Оновлюємо пакети
    sudo apt-get update

    # Встановлюємо Docker
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
else
    echo "Docker вже встановлений."
fi

# Завантажуємо образ Docker для Elixir validator (якщо ще не завантажено)
docker pull elixirprotocol/validator:v3 --platform linux/amd64

# Створюємо конфігураційні файли і запускаємо контейнери для кожної копії
for ((i=1; i<=CONTAINER_COUNT; i++))
do
    # Створюємо унікальний файл конфігурації для кожного контейнера
    ENV_FILE="/root/elxnode/validator_$i.env"
    echo "Створюємо файл $ENV_FILE"

    # Запитуємо інші значення у користувача
    read -p "Введіть STRATEGY_EXECUTOR_IP_ADDRESS: " STRATEGY_EXECUTOR_IP_ADDRESS
    read -p "Введіть STRATEGY_EXECUTOR_DISPLAY_NAME: " STRATEGY_EXECUTOR_DISPLAY_NAME
    read -p "Введіть STRATEGY_EXECUTOR_BENEFICIARY: " STRATEGY_EXECUTOR_BENEFICIARY
    read -p "Введіть SIGNER_PRIVATE_KEY: " SIGNER_PRIVATE_KEY

    # Записуємо ENV параметри в файл конфігурації
    echo "ENV=testnet-3" > $ENV_FILE
    echo "STRATEGY_EXECUTOR_IP_ADDRESS=$STRATEGY_EXECUTOR_IP_ADDRESS" >> $ENV_FILE
    echo "STRATEGY_EXECUTOR_DISPLAY_NAME=$STRATEGY_EXECUTOR_DISPLAY_NAME-$i" >> $ENV_FILE
    echo "STRATEGY_EXECUTOR_BENEFICIARY=$STRATEGY_EXECUTOR_BENEFICIARY" >> $ENV_FILE
    echo "SIGNER_PRIVATE_KEY=$SIGNER_PRIVATE_KEY" >> $ENV_FILE

    # Визначаємо порт для контейнера
    CONTAINER_PORT=$((START_PORT + i - 1))

    # Запускаємо контейнер для кожної конфігурації на унікальному порту
    echo "Запускаємо Docker контейнер $i на порту $CONTAINER_PORT..."
    docker run -d \
    -p $CONTAINER_PORT:17690 \
    --env-file $ENV_FILE \
    --name elixir_$i \
    --restart unless-stopped \
    elixirprotocol/validator:3
done

echo "Скрипт завершено. Усього запущено $CONTAINER_COUNT контейнерів Elixir."
