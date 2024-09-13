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

@router.get("/download_update_elxnode", response_class=Response)
async def download_update_elxnode():
    # Shell script content
    script_content = """
#!/bin/bash

echo "Оновлюємо систему Ubuntu..."
sudo apt update && sudo apt upgrade -y

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
	"""
    # Set content type for shell script
    return Response(content=script_content, media_type="text/x-sh", headers={
        "Content-Disposition": "attachment; filename=download_update_elxnode.sh"
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

# Запитуємо дані у користувача
read -p "Введіть ключ валідатора (якщо не введете, буде використаний ключ за замовчуванням): " validator_key
validator_key=${validator_key:-8888888888888888888888888888888888888888888888888888888888888888}

read -p "Введіть node-wallet-key: " node_wallet_key
read -p "Введіть IP адресу: " node_ip
read -p "Введіть ім'я ноди: " node_name
read -p "Введіть опис ноди: " node_description

# Оновлюємо систему
echo "Оновлюємо систему..."
sudo apt update && sudo apt upgrade -y

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

# Генеруємо конфігурацію валідатора
echo "Генеруємо конфігурацію валідатора..."
mkdir -p ~/hl/hyperliquid_data
echo "{\"key\": \"$validator_key\"}" > ~/hl/hyperliquid_data/node_config.json

# Запуск non-validator
echo "Запускаємо ноду в режимі non-validator..."
~/hl-visor run-non-validator &

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
echo "Валідатор налаштований. Можете слідкувати за його роботою через логи або підключитися до ноди."
	"""
    # Set content type for shell script
    return Response(content=script_content, media_type="text/x-sh", headers={
        "Content-Disposition": "attachment; filename=hyperliquid_dex.sh"
    })
