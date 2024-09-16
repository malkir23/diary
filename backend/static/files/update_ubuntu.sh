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
