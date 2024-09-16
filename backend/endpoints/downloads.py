from fastapi import APIRouter, Response
from starlette.responses import FileResponse
from backend.settings.config import settings
import os

def print_tree(startpath: str = '.', indent_level=0):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level + indent_level)
        print(f'{indent}├── {os.path.basename(root)}/')

        subindent = ' ' * 4 * (level + 1 + indent_level)
        for file in files:
            print(f'{subindent}└── {file}')


router = APIRouter()

@router.get("/download_sh", response_class=Response)
async def download_sh():
    file_name = 'download.sh'
    file_path = f'{settings.STATIC_FILES_ROOT}{file_name}'
    print_tree()
    return FileResponse(file_path, media_type='application/octet-stream',filename=file_name)


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
