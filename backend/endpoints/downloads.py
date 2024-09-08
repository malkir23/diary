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
