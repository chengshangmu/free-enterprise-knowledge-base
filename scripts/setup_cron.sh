#!/usr/bin/env bash
set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Configuring Crontab Schedules with CRON_TZ=Asia/Shanghai ==="

sudo bash -c "cat << EOF > /tmp/cron_schedule.txt
CRON_TZ=Asia/Shanghai
# 08:30 CST Daily Morning Knowledge Card
30 8 * * * cd ${APP_DIR} && ${APP_DIR}/venv/bin/python ${APP_DIR}/cron/daily_knowledge.py >> /var/log/daily_knowledge.log 2>&1
# 12:00 & 20:00 CST Self-Evolving Knowledge Harvester
0 12,20 * * * cd ${APP_DIR} && ${APP_DIR}/venv/bin/python ${APP_DIR}/harvester/knowledge_harvester.py >> /var/log/knowledge_harvester.log 2>&1
EOF
crontab /tmp/cron_schedule.txt
rm /tmp/cron_schedule.txt
"

sudo systemctl restart cron || sudo systemctl restart crond || true
echo "Crontab schedules successfully installed."
