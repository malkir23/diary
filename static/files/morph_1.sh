#!/bin/bash

# Оновлення системи та встановлення залежних компонентів
echo "Оновлюємо систему та встановлюємо залежності..."
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y make build-essential unzip lz4 gcc git jq ncdu tmux cmake clang pkg-config libssl-dev python3-pip protobuf-compiler bc curl

# Перевірка наявності Go
echo "Перевіряємо встановлену версію Go..."
GO_VERSION=$(go version 2>/dev/null)
REQUIRED_GO_VERSION="go1.22.2"

if [[ $GO_VERSION == *"$REQUIRED_GO_VERSION"* ]]; then
  echo "Необхідна версія Go ($REQUIRED_GO_VERSION) вже встановлена."
else
  echo "Необхідна версія Go ($REQUIRED_GO_VERSION) не встановлена. Встановлюємо..."
  sudo rm -rf /usr/local/go
  curl -Ls https://go.dev/dl/go1.22.2.linux-amd64.tar.gz | sudo tar -xzf - -C /usr/local
  echo 'export PATH=$PATH:/usr/local/go/bin' | sudo tee /etc/profile.d/golang.sh
  echo 'export PATH=$PATH:$HOME/go/bin' | tee -a $HOME/.profile
  source /etc/profile.d/golang.sh
  source ~/.profile
  go version
fi

# Створення каталогу для Morph та завантаження репозиторію
echo "Створюємо каталог для Morph та завантажуємо репозиторій..."
mkdir -p ~/.morph
cd ~/.morph
git clone https://github.com/morph-l2/morph.git
cd morph
git checkout v0.2.0-beta
make nccc_geth
cd ~/.morph/morph/node
make build

# Завантаження та розпакування файлів конфігурації Genesis блоку
echo "Завантажуємо та розпаковуємо конфігураційні файли Genesis блоку..."
cd ~/.morph
wget https://raw.githubusercontent.com/morph-l2/config-template/main/holesky/data.zip
unzip data.zip

# Створення секретного ключа
echo "Створюємо секретний ключ для зв'язку з вузлом..."
openssl rand -hex 32 > ~/.morph/jwt-secret.txt

# Завантаження та розпакування знімку (snapshot)
echo "Завантажуємо та розпаковуємо знімок..."
wget -q --show-progress https://snapshot.morphl2.io/holesky/snapshot-20240805-1.tar.gz
tar -xzvf snapshot-20240805-1.tar.gz
mv snapshot-20240805-1/geth geth-data
mv snapshot-20240805-1/data node-data
rm -rf snapshot-20240805-1.tar.gz

# Створення сервісного файлу для Geth
echo "Створюємо сервісний файл для Geth..."
sudo tee /etc/systemd/system/gethm.service > /dev/null << EOF
[Unit]
Description=Geth
After=network-online.target

[Service]
User=root
ExecStart=/root/.morph/morph/go-ethereum/build/bin/geth \
     --morph-holesky \
     --datadir "/root/.morph/geth-data" \
     --http --http.api=web3,debug,eth,txpool,net,engine \
     --http.port 8546 \
     --authrpc.addr localhost \
     --authrpc.vhosts="localhost" \
     --authrpc.port 8552 \
     --authrpc.jwtsecret=/root/.morph/jwt-secret.txt \
     --miner.gasprice="100000000" \
     --log.filename=/root/.morph/geth.log \
     --port 30363

Restart=on-failure
RestartSec=10
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

# Запуск сервісу Geth
echo "Запускаємо сервіс Geth..."
sudo systemctl daemon-reload
sudo systemctl enable gethm.service
sudo systemctl start gethm.service

# Створення сервісного файлу для Morph Node
echo "Створюємо сервісний файл для Morph Node..."
sudo tee /etc/systemd/system/morphm.service > /dev/null << EOF
[Unit]
Description=Morph Node
After=network-online.target

[Service]
User=root
ExecStart=/root/.morph/morph/node/build/bin/morphnode \
     --home /root/.morph/node-data \
     --l2.jwt-secret /root/.morph/jwt-secret.txt \
     --l2.eth http://localhost:8546 \
     --l2.engine http://localhost:8552 \
     --log.filename /root/.morph/node.log

Restart=on-failure
RestartSec=10
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

# Запуск сервісу Morph Node
echo "Запускаємо сервіс Morph Node..."
sudo systemctl daemon-reload
sudo systemctl enable morphm.service
sudo systemctl start morphm.service

echo "Установка завершена. Нода Morph та Geth запущені."
