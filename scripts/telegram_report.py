import psycopg2
import requests
import os
from datetime import datetime

# Telegram configuration from secrets
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram_message(message):
    """Send message to Telegram"""
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials not set")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.ok
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_report():
    """Generate report from database"""
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="queuepulse",
            user="queuepulse",
            password="queuepulse123"
        )
        cur = conn.cursor()
        
        # Get total orders
        cur.execute("SELECT COUNT(*) FROM dwh.fact_orders")
        total_orders = cur.fetchone()[0]
        
        # Get total revenue
        cur.execute("SELECT COALESCE(ROUND(SUM(amount)::numeric, 2), 0) FROM dwh.fact_orders")
        total_revenue = cur.fetchone()[0]
        
        # Get orders last 24h
        cur.execute("""
            SELECT COUNT(*), COALESCE(ROUND(SUM(amount)::numeric, 2), 0)
            FROM dwh.fact_orders
            WHERE processed_at >= NOW() - INTERVAL '24 hours'
        """)
        last_24h_orders, last_24h_revenue = cur.fetchone()
        
        conn.close()
        
        now = datetime.now()
        
        report = f"""
******************************************
║     QUEUEPULSE REPORT                    ║
║     {now.strftime('%Y-%m-%d %H:%M:%S')}          ║
******************************************

TOTAL STATISTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Orders: {total_orders:,}
• Total Revenue: ${total_revenue:,.2f}

 LAST 24 HOURS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Orders: {last_24h_orders:,}
• Revenue: ${last_24h_revenue:,.2f}

System: OPERATIONAL
DWH: ACTIVE
"""
        return report
    except Exception as e:
        return f"Database error: {e}"

if __name__ == "__main__":
    print("Generating report...")
    report = get_report()
    print(report)
    send_telegram_message(report)
