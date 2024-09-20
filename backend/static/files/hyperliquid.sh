#!/bin/bash

# Запитуємо дані у користувача
read -p "Введіть ключ валідатора (якщо не введете, буде використаний ключ за замовчуванням): " validator_key
validator_key=${validator_key:-8888888888888888888888888888888888888888888888888888888888888888}

read -p "Введіть node-wallet-key: " node_wallet_key
read -p "Введіть IP адресу: " node_ip
read -p "Введіть ім'я ноди: " node_name
read -p "Введіть опис ноди: " node_description

# Встановлюємо Docker, якщо він не встановлений
if ! [ -x "$(command -v docker)" ]; then
    echo "Встановлюємо Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
else
    echo "Docker вже встановлений."
fi

# Налаштування ланцюга на Testnet
echo '{"chain": "Testnet"}' > ~/visor.json

# Завантажуємо і встановлюємо hl-visor
echo "Завантажуємо hl-visor..."
curl https://binaries.hyperliquid.xyz/Testnet/hl-visor > ~/hl-visor
chmod a+x ~/hl-visor

# Клонування репозиторію Hyperliquid
echo "Клонуємо репозиторій Hyperliquid..."
git clone https://github.com/hyperliquid-dex/node
cd node

# Редагування Dockerfile для запуску в режимі non-validator
echo "Редагуємо Dockerfile..."
sed -i 's#ENTRYPOINT \[.*\]#ENTRYPOINT \["/home/hluser/hl-visor", "run-non-validator"\]#' Dockerfile

# Генеруємо конфігурацію валідатора
echo "Генеруємо конфігурацію валідатора..."
mkdir -p ~/hl/hyperliquid_data
echo "{\"key\": \"$validator_key\"}" > ~/hl/hyperliquid_data/node_config.json

# Створюємо Docker image
echo "Створюємо Docker image..."
docker compose build

# Запуск Docker контейнера
echo "Запускаємо Docker контейнер..."
docker compose up -d

# Створюємо файл для швидшого завантаження з відомого peer
echo '{ "root_node_ips": [{"Ip": "1.2.3.4"}], "try_new_peers": false }' > ~/override_gossip_config.json

# Друк адреси валідатора
echo "Адреса вашого валідатора:"
~/hl-node --chain Testnet print-address $node_wallet_key

# Реєструємо публічну IP адресу валідатора
echo "Реєстрація публічної IP адреси валідатора..."
~/hl-node --chain Testnet send-signed-action "{\"type\": \"CValidatorAction\", \"register\": {\"profile\": {\"node_ip\": {\"Ip\": \"$node_ip\"}, \"name\": \"$node_name\", \"description\": \"$node_description\"}}}" $node_wallet_key

# Відкриваємо порти для валідатора
echo "Відкриваємо порти для валідатора..."
sudo ufw allow 4000
sudo ufw allow 5000
sudo ufw allow 6000
sudo ufw allow 7000
sudo ufw allow 8000
sudo ufw allow 9000
sudo ufw enable

# Завершення
echo "Валідатор налаштований і запущений. Ви можете перевірити роботу через Docker та переглянути логи."
echo "Команда для перегляду логів: docker logs -f hyperliquid-node-1"
