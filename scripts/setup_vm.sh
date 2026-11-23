#!/usr/bin/env bash
set -e

echo "=== [1/4] Configuring Linux 4GB Swap ==="
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "Swap configured successfully."
else
    echo "Swap already exists."
fi

echo "=== [2/4] Enabling BBR Congestion Control ==="
sudo modprobe tcp_bbr || true
if ! grep -q "net.core.default_qdisc=fq" /etc/sysctl.conf; then
    echo "net.core.default_qdisc=fq" | sudo tee -a /etc/sysctl.conf
    echo "net.ipv4.tcp_congestion_control=bbr" | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p
fi

echo "=== [3/4] Locking Timezone to Asia/Shanghai ==="
sudo timedatectl set-timezone Asia/Shanghai

echo "=== [4/4] Installing Python Virtualenv & System Packages ==="
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv

echo "VM optimization completed successfully!"
