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
