import psycopg2
import requests
import os
from datetime import datetime

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8992445678:AAFFz-SceU04rDvJgd0o7Gh4CHBbZHbdjUA')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '8992445678') 

def send_report():
    """Send current database report to Telegram"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="queuepulse",
            user="queuepulse",
            password="queuepulse123"
        )
        cur = conn.cursor()
        
        # Get statistics
        cur.execute("SELECT COUNT(*) FROM dwh.fact_orders")
        total_orders = cur.fetchone()[0]
        
        cur.execute("SELECT COALESCE(ROUND(SUM(amount)::numeric, 2), 0) FROM dwh.fact_orders")
        total_revenue = cur.fetchone()[0]
        
        cur.execute("SELECT COALESCE(ROUND(AVG(amount)::numeric, 2), 0) FROM dwh.fact_orders")
        avg_order = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM dwh.fact_orders")
        unique_customers = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*), COALESCE(ROUND(SUM(amount)::numeric, 2), 0)
            FROM dwh.fact_orders
            WHERE processed_at >= NOW() - INTERVAL '24 hours'
        """)
        last_24h_orders, last_24h_revenue = cur.fetchone()
        
        conn.close()
        
        now = datetime.now()
        
        report = f"""
*****************************************
║     QUEUEPULSE MANUAL REPORT             ║
║     {now.strftime('%Y-%m-%d %H:%M:%S')}          ║
******************************************

 TOTAL STATISTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Orders: {total_orders:,}
• Total Revenue: ${total_revenue:,.2f}
• Average Order: ${avg_order:.2f}
• Unique Customers: {unique_customers:,}

LAST 24 HOURS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Orders: {last_24h_orders:,}
• Revenue: ${last_24h_revenue:,.2f}

System: OPERATIONAL
DWH: ACTIVE
"""
        # Send to Telegram
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        response = requests.post(url, json={'chat_id': CHAT_ID, 'text': report})
        
        if response.ok:
            print("Report sent to Telegram!")
        else:
            print(f"Failed to send: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_report()
