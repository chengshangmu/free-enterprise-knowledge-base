#!/usr/bin/env bash
set -e

SERVICE_PATH="/etc/systemd/system/wechat-bot.service"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Registering Systemd Service at ${SERVICE_PATH} ==="

sudo bash -c "cat << EOF > ${SERVICE_PATH}
[Unit]
Description=Free-Tier Enterprise WeChat AI Knowledge Bot
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/uvicorn core.bot_gateway:app --host 0.0.0.0 --port 80
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable wechat-bot
sudo systemctl restart wechat-bot

echo "Service successfully installed and started."
