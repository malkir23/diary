#!/bin/bash

# Зупинка раніше створених служб
echo "Зупинка служб Geth та Morph..."
sudo systemctl stop gethm
sudo systemctl stop morphm

# Створення нового сервісного файлу для Geth Validator
echo "Створюємо сервісний файл для Geth Validator..."
sudo tee /etc/systemd/system/geth_morph.service > /dev/null << EOF
[Unit]
Description=Geth for Validator
After=network-online.target

[Service]
User=root
ExecStart=/root/.morph/morph/go-ethereum/build/bin/geth \
--datadir=/root/.morph/geth-data \
--port 30305 \
--verbosity=3 \
--http \
--http.corsdomain="*" \
--http.vhosts="*" \
--http.addr=0.0.0.0 \
--http.port=8547 \
--http.api=web3,eth,txpool,net,engine \
--ws \
--ws.addr=0.0.0.0 \
--ws.port=8546 \
--ws.origins="*" \
--ws.api=web3,eth,txpool,net,engine \
--networkid=2810 \
--authrpc.addr="0.0.0.0" \
--authrpc.port="8552" \
--authrpc.vhosts="*" \
--authrpc.jwtsecret=/root/.morph/jwt-secret.txt \
--gcmode=archive \
--metrics \
--metrics.addr=0.0.0.0 \
--metrics.port=6063 \
--miner.gasprice="100000000"

Restart=on-failure
RestartSec=10
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

# Запуск нової служби Geth
echo "Запускаємо нову службу Geth..."
sudo systemctl daemon-reload
sudo systemctl enable geth_morph
sudo systemctl start geth_morph

# Перевірка та налаштування змінних середовища
echo "Налаштовуємо змінні середовища..."
export L1MessageQueueWithGasPriceOracle=0x778d1d9a4d8b6b9ade36d967a9ac19455ec3fd0b
export START_HEIGHT=1434640
export Rollup=0xd8c5c541d56f59d65cf775de928ccf4a47d4985c
export Ethereum_Holesky_beacon_chain_RPC=https://ethereum-holesky-beacon-api.publicnode.com

# Користувач має вказати свої дані
read -p "Введіть свій Ethereum Holesky RPC (отриманий на Infura): " Ethereum_Holesky_RPC
read -p "Введіть приватний ключ валідатора: " Your_Validator_Key

export Ethereum_Holesky_RPC=$Ethereum_Holesky_RPC
export Your_Validator_Key=$Your_Validator_Key

# Створення сервісного файлу для Morph Validator
echo "Створюємо сервісний файл для Morph Validator..."
sudo tee /etc/systemd/system/morph_validator.service > /dev/null << EOF
[Unit]
Description=Morph Validator Node
After=network-online.target

[Service]
User=root
ExecStart=/root/.morph/morph/node/build/bin/morphnode --validator --home /root/.morph/node-data \
 --l2.jwt-secret /root/.morph/jwt-secret.txt \
 --l2.eth http://localhost:8547 \
 --l2.engine http://localhost:8552 \
 --l1.rpc $Ethereum_Holesky_RPC \
 --l1.beaconrpc $Ethereum_Holesky_beacon_chain_RPC \
 --l1.chain-id 17000 \
 --validator.privateKey $Your_Validator_Key \
 --sync.depositContractAddr $L1MessageQueueWithGasPriceOracle \
 --sync.startHeight $START_HEIGHT \
 --derivation.rollupAddress $Rollup \
 --derivation.startHeight $START_HEIGHT \
 --derivation.fetchBlockRange 200 \
 --log.filename /root/.morph/node.log \
 --metrics-server-enable

Restart=on-failure
RestartSec=10
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

# Запуск нової служби Morph Validator
echo "Запускаємо нову службу Morph Validator..."
sudo systemctl daemon-reload
sudo systemctl enable morph_validator
sudo systemctl start morph_validator

echo "Усі служби запущені успішно."
