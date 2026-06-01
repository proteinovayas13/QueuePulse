import requests
from datetime import datetime

BOT_TOKEN = "8992445678:AAFFz-SceU04rDvJgd0o7Gh4CHBbZHbdjUA"
CHAT_ID = "6159736716"  

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_dashboard_link():
    github_url = "https://YOUR_USERNAME.github.io/queuepulse/"
    local_url = "http://localhost:5000"
    
    message = f"""
**********************************************
QUEUEPULSE DASHBOARD
**********************************************

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Live Dashboard URLs:

[1] GitHub Pages (Public):
{github_url}

[2] Local Server (Requires VPN):
{local_url}

Features:
- Total Orders and Revenue
- CPU Usage Monitoring
- RabbitMQ Queue Status
- Top Products Ranking
- System Health Status

Dashboard updates every 30 seconds
**********************************************
"""
    
    result = send_telegram_message(message)
    if result and result.get('ok'):
        print("Dashboard link sent to Telegram")
    else:
        print("Failed to send")

if __name__ == "__main__":
    send_dashboard_link()
