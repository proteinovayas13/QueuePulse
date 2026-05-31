# scripts/telegram_daily_report.py
import psycopg2
import requests
import os
from datetime import datetime

# Telegram configuration from secrets
BOT_TOKEN = os.environ.get('8992445678:AAFFz-SceU04rDvJgd0o7Gh4CHBbZHbdjUA')
CHAT_ID = os.environ.get('8992445678')

def get_dwh_metrics():
    """Get metrics from DWH"""
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="queuepulse",
            user="queuepulse",
            password="queuepulse123"
        )
        cur = conn.cursor()
        
        # Total metrics
        cur.execute("SELECT COUNT(*) FROM dwh.fact_orders")
        total_orders = cur.fetchone()[0]
        
        cur.execute("SELECT ROUND(SUM(amount)::numeric, 2) FROM dwh.fact_orders")
        total_revenue = cur.fetchone()[0] or 0
        
        cur.execute("SELECT ROUND(AVG(amount)::numeric, 2) FROM dwh.fact_orders")
        avg_order = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM dwh.fact_orders")
        unique_customers = cur.fetchone()[0]
        
        # Last 24 hours
        cur.execute("""
            SELECT COUNT(*), ROUND(SUM(amount)::numeric, 2)
            FROM dwh.fact_orders
            WHERE processed_at >= NOW() - INTERVAL '24 hours'
        """)
        last_24h_orders, last_24h_revenue = cur.fetchone()
        last_24h_orders = last_24h_orders or 0
        last_24h_revenue = last_24h_revenue or 0
        
        # Top products
        cur.execute("""
            SELECT product_id, COUNT(*) as orders, ROUND(SUM(amount)::numeric, 2) as revenue
            FROM dwh.fact_orders
            GROUP BY product_id
            ORDER BY revenue DESC
            LIMIT 5
        """)
        top_products = cur.fetchall()
        
        conn.close()
        
        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'avg_order': avg_order,
            'unique_customers': unique_customers,
            'last_24h_orders': last_24h_orders,
            'last_24h_revenue': last_24h_revenue,
            'top_products': top_products
        }
    except Exception as e:
        print(f"Database error: {e}")
        return None

def send_telegram_message(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def create_daily_report():
    """Create daily report message"""
    metrics = get_dwh_metrics()
    if not metrics:
        return "Database connection failed!"
    
    now = datetime.now()
    
    # Format top products
    products_text = ""
    for i, (prod_id, orders, revenue) in enumerate(metrics['top_products'], 1):
        products_text += f"{i}. {prod_id}: {orders} orders (${revenue:,.2f})\n"
    
    report = f"""
*******************************************
     QUEUEPULSE DAILY REPORT              
    {now.strftime('%Y-%m-%d %H:%M:%S')}          
*******************************************

TOTAL STATISTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Orders: {metrics['total_orders']:,}
• Total Revenue: ${metrics['total_revenue']:,.2f}
• Average Order: ${metrics['avg_order']:.2f}
• Unique Customers: {metrics['unique_customers']:,}

LAST 24 HOURS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Orders: {metrics['last_24h_orders']:,}
• Revenue: ${metrics['last_24h_revenue']:,.2f}

TOP 5 PRODUCTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{products_text}
 Status: All systems operational
 DWH: Active and processing data
"""
    return report

if __name__ == "__main__":
    report = create_daily_report()
    send_telegram_message(report)