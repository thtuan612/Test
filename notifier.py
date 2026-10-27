import requests
from datetime import datetime
from zoneinfo import ZoneInfo

VIETNAM = ZoneInfo("Asia/Ho_Chi_Minh")


def send_code_notification(webhook_url, item):
    code = item["code"]
    reward = item.get("reward") or "Chưa xác định"
    status = item.get("status") or "Chưa xác định"
    now = datetime.now(VIETNAM).strftime("%d/%m/%Y %H:%M:%S")

    embed = {
        "title": "🎁 Giftcode mới được phát hiện!",
        "url": item.get("source_url") or "https://codes.yar.gg/",
        "color": 0x57F287,
        "fields": [
            {"name": "🎟️ Code", "value": f"```{code[:100]}```", "inline": False},
            {"name": "🎁 Phần thưởng", "value": str(reward)[:1024], "inline": False},
            {"name": "📌 Trạng thái", "value": str(status)[:200], "inline": True},
            {"name": "🕒 Phát hiện lúc", "value": now, "inline": True},
        ],
        "footer": {"text": "Nguồn: codes.yar.gg"},
    }
    response = requests.post(
        webhook_url,
        json={"username": "YAR Giftcode Monitor", "embeds": [embed]},
        timeout=20,
    )
    response.raise_for_status()
