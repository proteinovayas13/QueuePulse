import requests
import subprocess
from datetime import datetime

BOT_TOKEN = "8992445678:AAFFz-SceU04rDvJgd0o7Gh4CHBbZHbdjUA"
CHAT_ID = 6159736716  # Ваш правильный Chat ID

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.ok:
            print("Message sent to Telegram!")
        else:
            print(f"Failed: {response.text}")
        return response.ok
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_sql(query):
    result = subprocess.run(
        ['docker', 'exec', 'queuepulse-postgres', 'psql', '-U', 'queuepulse', '-d', 'queuepulse', '-t', '-c', query],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout.strip()

def get_dwh_stats():
    try:
        total_orders = int(run_sql("SELECT COUNT(*) FROM dwh.fact_orders") or 0)
        total_revenue = float(run_sql("SELECT COALESCE(ROUND(SUM(amount)::numeric, 2), 0) FROM dwh.fact_orders") or 0)
        avg_order = float(run_sql("SELECT COALESCE(ROUND(AVG(amount)::numeric, 2), 0) FROM dwh.fact_orders") or 0)
        unique_users = int(run_sql("SELECT COUNT(DISTINCT user_id) FROM dwh.fact_orders") or 0)
        
        last_24h_result = run_sql("SELECT COUNT(*) || '|' || COALESCE(ROUND(SUM(amount)::numeric, 2), 0) FROM dwh.fact_orders WHERE processed_at >= NOW() - INTERVAL '24 hours'")
        if '|' in last_24h_result:
            parts = last_24h_result.split('|')
            last_24h_orders = int(parts[0] or 0)
            last_24h_revenue = float(parts[1] or 0)
        else:
            last_24h_orders = 0
            last_24h_revenue = 0
        
        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'avg_order': avg_order,
            'unique_users': unique_users,
            'last_24h_orders': last_24h_orders,
            'last_24h_revenue': last_24h_revenue
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return None

def send_report():
    stats = get_dwh_stats()
    if not stats:
        print("Failed to get stats")
        return
    
    now = datetime.now()
    
    report = f"""
*******************************************
     QUEUEPULSE DWH REPORT
     {now.strftime('%Y-%m-%d %H:%M:%S')}
*******************************************

TOTAL STATISTICS:
*******************************************
Total Orders:     {stats['total_orders']:,}
Total Revenue:    ${stats['total_revenue']:,.2f}
Average Order:    ${stats['avg_order']:.2f}
Unique Customers: {stats['unique_users']:,}

LAST 24 HOURS:
*******************************************
Orders:  {stats['last_24h_orders']:,}
Revenue: ${stats['last_24h_revenue']:,.2f}

STATUS: OPERATIONAL
*******************************************
"""
    
    send_telegram_message(report)

if __name__ == "__main__":
    send_report()
