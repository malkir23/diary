from fastapi import APIRouter, Response


router = APIRouter()

@router.get("/download_sh", response_class=Response)
async def download_sh():
    # Shell script content
    script_content = """
		#!/bin/bash

		# Оновлюємо пакети
		echo "Оновлення списку пакетів..."
		sudo apt update

		# Встановлюємо OpenSSH Server, якщо він не встановлений
		if ! dpkg -l | grep -q openssh-server; then
			echo "Встановлення OpenSSH Server..."
			sudo apt install -y openssh-server
		else
			echo "OpenSSH Server вже встановлений."
		fi

		# Запускаємо та включаємо службу SSH
		echo "Запуск та активація SSH служби..."
		sudo systemctl enable ssh
		sudo systemctl start ssh

		# Перевіряємо статус SSH
		echo "Статус SSH служби:"
		sudo systemctl status ssh | grep "active (running)"

		# Відкриваємо порт 22 у брандмауері UFW (якщо використовується UFW)
		if sudo ufw status | grep -q "inactive"; then
			echo "Брандмауер UFW не активний."
		else
			echo "Відкриття порту 22 у брандмауері..."
			sudo ufw allow 22
			sudo ufw reload
		fi

		echo "SSH готовий до використання. Можете підключатися."
	"""
    # Set content type for shell script
    return Response(content=script_content, media_type="text/x-sh", headers={
        "Content-Disposition": "attachment; filename=sample-script.sh"
    })


@router.get("/download_elxnode", response_class=Response)
async def download_elxnode():
    # Shell script content
    script_content = """
#!/bin/bash

# Створюємо папку elxnode в корені
mkdir -p /root/elxnode

# Створюємо файл validator.env
ENV_FILE="/root/elxnode/validator.env"

echo "Створюємо файл $ENV_FILE"

# Записуємо ENV параметр
echo "ENV=testnet-3" > $ENV_FILE

# Запитуємо інші значення у користувача
read -p "Введіть STRATEGY_EXECUTOR_IP_ADDRESS: " STRATEGY_EXECUTOR_IP_ADDRESS
read -p "Введіть STRATEGY_EXECUTOR_DISPLAY_NAME: " STRATEGY_EXECUTOR_DISPLAY_NAME
read -p "Введіть STRATEGY_EXECUTOR_BENEFICIARY: " STRATEGY_EXECUTOR_BENEFICIARY
read -p "Введіть SIGNER_PRIVATE_KEY: " SIGNER_PRIVATE_KEY

# Додаємо ці значення у файл validator.env
echo "STRATEGY_EXECUTOR_IP_ADDRESS=$STRATEGY_EXECUTOR_IP_ADDRESS" >> $ENV_FILE
echo "STRATEGY_EXECUTOR_DISPLAY_NAME=$STRATEGY_EXECUTOR_DISPLAY_NAME" >> $ENV_FILE
echo "STRATEGY_EXECUTOR_BENEFICIARY=$STRATEGY_EXECUTOR_BENEFICIARY" >> $ENV_FILE
echo "SIGNER_PRIVATE_KEY=$SIGNER_PRIVATE_KEY" >> $ENV_FILE

# Встановлюємо Docker
echo "Встановлюємо Docker..."

# Додаємо офіційний ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Додаємо репозиторій Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Оновлюємо пакети
sudo apt-get update

# Встановлюємо Docker
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Завантажуємо образ Docker для Elixir validator
docker pull elixirprotocol/validator:v3 --platform linux/amd64

# Запускаємо контейнер в фоновому режимі
docker run -d \
--env-file /root/elxnode/validator.env \
--name elixir \
--restart unless-stopped \
elixirprotocol/validator:3.4.0

# Запускаємо інтерактивний режим контейнера
docker run -it \
--env-file /root/elxnode/validator.env \
--name elixir \
elixirprotocol/validator:3.4.0

echo "Скрипт завершено. Контейнер Elixir запущено."
	"""
    # Set content type for shell script
    return Response(content=script_content, media_type="text/x-sh", headers={
        "Content-Disposition": "attachment; filename=elxnode-script.sh"
    })


@router.get("/download_update_ubuntu", response_class=Response)
async def download_update_ubuntu():
    # Shell script content
    script_content = """
#!/bin/bash

# Оновлюємо списки пакетів
echo "Оновлюємо пакети..."
sudo apt update -y && sudo apt upgrade -y

# Перевірка поточної версії Ubuntu
echo "Поточна версія Ubuntu:"
lsb_release -a

# Оновлення до наступної версії Ubuntu (спочатку до 22.10, а потім до 24.04)
echo "Починаємо процес оновлення до наступної версії Ubuntu..."

# Встановлюємо update-manager-core, якщо не встановлено
sudo apt install update-manager-core -y

# Виконуємо попереднє оновлення (до 22.10)
sudo do-release-upgrade -d -f DistUpgradeViewNonInteractive

# Перевіряємо успішність оновлення та пропонуємо продовжити до Ubuntu 24
if [ $(lsb_release -rs) == "22.10" ]; then
    echo "Оновлено до Ubuntu 22.10. Продовжуємо до Ubuntu 24.04..."
    sudo do-release-upgrade -d -f DistUpgradeViewNonInteractive
else
    echo "Помилка: не вдалося оновити до Ubuntu 22.10"
    exit 1
fi

# Перевірка остаточної версії після оновлення
echo "Перевірка версії після оновлення:"
lsb_release -a
	"""
    # Set content type for shell script
    return Response(content=script_content, media_type="text/x-sh", headers={
        "Content-Disposition": "attachment; filename=update_ubuntu.sh"
    })


@router.get("/download_hyperliquid_dex", response_class=Response)
async def download_hyperliquid_dex():
    # Shell script content
    script_content = """
#!/bin/bash

# Запитуємо ключ валідатора у користувача
read -p "Введіть ключ валідатора (за замовчуванням: 8888888888888888888888888888888888888888888888888888888888888888): " node_wallet_key

# Використовуємо ключ за замовчуванням, якщо користувач нічого не ввів
node_wallet_key=${node_wallet_key:-8888888888888888888888888888888888888888888888888888888888888888}

# Створюємо конфігураційний файл для ланцюга Testnet
echo "Налаштовуємо ланцюг на Testnet..."
echo '{"chain": "Testnet"}' > ~/visor.json

# Завантажуємо бінарний файл visor і робимо його виконуваним
echo "Завантажуємо visor..."
curl -fsSL https://binaries.hyperliquid.xyz/Testnet/hl-visor > ~/hl-visor && chmod a+x ~/hl-visor

# Перевіряємо, чи все працює для non-validator
echo "Запуск non-validator..."
~/hl-visor run-non-validator &

# Створюємо каталоги для даних
mkdir -p ~/hl/data/replica_cmds ~/hl/data/periodic_abci_states ~/hl/data/node_trades ~/hl/data/node_order_statuses ~/hl/data/consensus

# Налаштовуємо порти 4000-9000 для валідатора
echo "Налаштовуємо відкриття портів для валідатора..."
for port in {4000..9000}
do
    sudo ufw allow $port
done

# Перевірка стану портів 8 і 9000
echo "Перевіряємо порти 8 і 9000..."
check_port_usage() {
    PORT=$1
    if sudo lsof -i -P -n | grep LISTEN | grep ":$PORT"; then
        echo "Порт $PORT використовується."
    else
        echo "Порт $PORT не використовується."
    fi
}

check_port_usage 8
check_port_usage 9000

# Перевіряємо стан портів у брандмауері
check_port_firewall() {
    PORT=$1
    if sudo ufw status | grep "$PORT"; then
        echo "Порт $PORT відкритий у брандмауері."
    else
        echo "Порт $PORT закритий у брандмауері."
    fi
}

check_port_firewall 8
check_port_firewall 9000

# Опціональний крок для включення EVM
read -p "Чи бажаєте увімкнути EVM RPC? (y/n): " enable_evm
if [ "$enable_evm" == "y" ]; then
    echo "Запуск non-validator з EVM RPC..."
    ~/hl-visor run-non-validator --evm &
    echo "EVM RPC працює на localhost:3001"
fi

# Опціональний крок для запису ордерів
read -p "Чи бажаєте увімкнути запис ордерів? (y/n): " enable_orders
if [ "$enable_orders" == "y" ]; then
    echo "Запуск non-validator з опцією запису ордерів..."
    ~/hl-visor run-non-validator --write-order-statuses &
fi

# Налаштовуємо валідатор
read -p "Чи бажаєте налаштувати та запустити валідатор? (y/n): " setup_validator
if [ "$setup_validator" == "y" ]; then
    # Створюємо конфіг файл для валідатора з ключем, який ввів користувач
    echo '{"key": "'"$node_wallet_key"'"}' > ~/hl/hyperliquid_data/node_config.json

    # Показуємо адресу валідатора
    echo "Адреса валідатора:"
    ~/hl-node --chain Testnet print-address $node_wallet_key

    # Запитуємо IP валідатора, ім'я і опис
    read -p "Введіть публічну IP адресу вашого валідатора: " validator_ip
    read -p "Введіть ім'я валідатора: " validator_name
    read -p "Введіть опис валідатора: " validator_description

    # Реєструємо валідатора
    ~/hl-node --chain Testnet send-signed-action "{\"type\": \"CValidatorAction\", \"register\": {\"profile\": {\"node_ip\": {\"Ip\": \"$validator_ip\"}, \"name\": \"$validator_name\", \"description\": \"$validator_description\" }}}" $node_wallet_key

    # Завантажуємо та запускаємо валідатор
    echo "Запуск валідатора..."
    curl -fsSL https://binaries.hyperliquid.xyz/Testnet/hl-visor > ~/hl-visor && chmod a+x ~/hl-visor
    ~/hl-visor run-validator &

    # Реєструємо в системі
    echo '{ "root_node_ips": [{"Ip": "1.2.3.4"}], "try_new_peers": false }' > ~/override_gossip_config.json

    echo "Валідатор налаштований і запущений."
fi

echo "Скрипт завершено."
	"""
    # Set content type for shell script
    return Response(content=script_content, media_type="text/x-sh", headers={
        "Content-Disposition": "attachment; filename=hyperliquid_dex.sh"
    })
