import requests
import subprocess
from datetime import datetime

# Get credentials from environment or use defaults
BOT_TOKEN = "8992445678:AAFFz-SceU04rDvJgd0o7Gh4CHBbZHbdjUA"
CHAT_ID = 6159736716

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={'chat_id': CHAT_ID, 'text': text}, timeout=10)
        if r.ok:
            print("Message sent!")
        else:
            print(f"Failed: {r.text}")
        return r.ok
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_stats():
    try:
        orders = subprocess.run(
            ['docker', 'exec', 'queuepulse-postgres', 'psql', '-U', 'queuepulse', '-d', 'queuepulse', '-t', '-c', 
             'SELECT COUNT(*) FROM dwh.fact_orders'],
            capture_output=True, text=True, timeout=30
        ).stdout.strip() or "0"
        
        revenue = subprocess.run(
            ['docker', 'exec', 'queuepulse-postgres', 'psql', '-U', 'queuepulse', '-d', 'queuepulse', '-t', '-c', 
             'SELECT COALESCE(ROUND(SUM(amount)::numeric, 2), 0) FROM dwh.fact_orders'],
            capture_output=True, text=True, timeout=30
        ).stdout.strip() or "0"
        
        return orders, revenue
    except Exception as e:
        print(f"Error getting stats: {e}")
        return "0", "0"

if __name__ == "__main__":
    orders, revenue = get_stats()
    now = datetime.now()
    
    message = f"""
========================================
QUEUEPULSE DWH REPORT
{now.strftime('%Y-%m-%d %H:%M:%S')}
========================================

TOTAL STATISTICS:
----------------------------------------
Total Orders: {int(orders):,}
Total Revenue: ${float(revenue):,.2f}

STATUS: OPERATIONAL
========================================
"""
    print(message)
    send_message(message)
