#!/bin/bash

# Створюємо папку elxnode в корені
mkdir -p /root/elxnode

# Запитуємо кількість Docker копій у користувача
read -p "Введіть кількість Docker копій (контейнерів): " CONTAINER_COUNT

# Запитуємо інші значення у користувача
read -p "Введіть STRATEGY_EXECUTOR_IP_ADDRESS: " STRATEGY_EXECUTOR_IP_ADDRESS
read -p "Введіть STRATEGY_EXECUTOR_DISPLAY_NAME: " STRATEGY_EXECUTOR_DISPLAY_NAME
read -p "Введіть STRATEGY_EXECUTOR_BENEFICIARY: " STRATEGY_EXECUTOR_BENEFICIARY
read -p "Введіть SIGNER_PRIVATE_KEY: " SIGNER_PRIVATE_KEY

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

    # Записуємо ENV параметри в файл конфігурації
    echo "ENV=testnet-3" > $ENV_FILE
    echo "STRATEGY_EXECUTOR_IP_ADDRESS=$STRATEGY_EXECUTOR_IP_ADDRESS" >> $ENV_FILE
    echo "STRATEGY_EXECUTOR_DISPLAY_NAME=$STRATEGY_EXECUTOR_DISPLAY_NAME-$i" >> $ENV_FILE
    echo "STRATEGY_EXECUTOR_BENEFICIARY=$STRATEGY_EXECUTOR_BENEFICIARY" >> $ENV_FILE
    echo "SIGNER_PRIVATE_KEY=$SIGNER_PRIVATE_KEY" >> $ENV_FILE

    # Запускаємо контейнер для кожної конфігурації
    echo "Запускаємо Docker контейнер $i..."
    docker run -d \
    --env-file $ENV_FILE \
    --name elixir_$i \
    --restart unless-stopped \
    elixirprotocol/validator:3.4.0
done

echo "Скрипт завершено. Усього запущено $CONTAINER_COUNT контейнерів Elixir."
