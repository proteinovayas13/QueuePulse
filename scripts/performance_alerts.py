# scripts/performance_alerts.py
import psycopg2
import requests
import os
import time
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_alert(message):
    """Send alert to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': f"🚨 PERFORMANCE ALERT 🚨\n\n{message}\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        'parse_mode': 'HTML'
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error: {e}")

def check_performance():
    """Check performance metrics"""
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="queuepulse",
            user="queuepulse",
            password="queuepulse123"
        )
        cur = conn.cursor()
        
        # Check orders in last hour
        cur.execute("""
            SELECT COUNT(*)
            FROM dwh.fact_orders
            WHERE processed_at >= NOW() - INTERVAL '1 hour'
        """)
        last_hour_orders = cur.fetchone()[0] or 0
        
        if last_hour_orders == 0:
            send_alert("No orders in the last hour!")
        
        # Check average processing time
        cur.execute("""
            SELECT AVG(EXTRACT(EPOCH FROM (processed_at - created_at)))
            FROM dwh.fact_orders
            WHERE processed_at >= NOW() - INTERVAL '1 hour'
        """)
        avg_processing = cur.fetchone()[0] or 0
        
        if avg_processing > 5:
            send_alert(f"High processing time! Average: {avg_processing:.1f} seconds")
        
        # Check success rate
        cur.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'PROCESSED' THEN 1 END)::float / COUNT(*) * 100
            FROM dwh.fact_orders
            WHERE processed_at >= NOW() - INTERVAL '1 hour'
        """)
        success_rate = cur.fetchone()[0] or 100
        
        if success_rate < 95:
            send_alert(f"Low success rate! {success_rate:.1f}%")
        
        # Check queue size in RabbitMQ (via API)
        try:
            import requests
            from requests.auth import HTTPBasicAuth
            response = requests.get('http://localhost:15672/api/queues',
                                   auth=HTTPBasicAuth('admin', 'admin123'), timeout=5)
            if response.status_code == 200:
                queues = response.json()
                for queue in queues:
                    if queue.get('name') == 'order.queue':
                        messages = queue.get('messages_ready', 0)
                        if messages > 100:
                            send_alert(f"Queue backlog! {messages} messages waiting")
        except:
            pass
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_performance()