import requests
import json
import time
import random
import psycopg2
import os
from datetime import datetime

# Telegram configuration
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8992445678:AAFFz-SceU04rDvJgd0o7Gh4CHBbZHbdjUA')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')  # Replace with your chat ID

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
        return response.ok
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def generate_orders(count=1000):
    """Generate test orders"""
    print(f"Generating {count} orders...")
    
    success_count = 0
    for i in range(count):
        try:
            # Generate random order
            order = {
                "userId": f"user_{random.randint(1, 100)}",
                "amount": round(random.uniform(10, 1000), 2),
                "productId": f"prod_{random.randint(1, 50):04d}"
            }
            
            # Send to producer
            response = requests.post(
                "http://localhost:8080/api/orders",
                json=order,
                timeout=5
            )
            
            if response.status_code == 200:
                success_count += 1
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{count}")
                
        except Exception as e:
            print(f"  Error on order {i}: {e}")
        
        # Small delay to not overload
        time.sleep(0.01)
    
    print(f"\nCompleted: {success_count}/{count} successful")
    
    # Send report after generation
    send_generation_report(success_count, count)
    
    return success_count

def send_generation_report(success, total):
    """Send report about data generation"""
    
    # Get current database stats
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="queuepulse",
            user="queuepulse",
            password="queuepulse123"
        )
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM dwh.fact_orders")
        total_orders = cur.fetchone()[0]
        
        cur.execute("SELECT COALESCE(ROUND(SUM(amount)::numeric, 2), 0) FROM dwh.fact_orders")
        total_revenue = cur.fetchone()[0]
        
        conn.close()
        
        now = datetime.now()
        
        report = f"""
*******************************************
║     QUEUEPULSE DATA GENERATION REPORT    ║
║     {now.strftime('%Y-%m-%d %H:%M:%S')}          ║
*******************************************

GENERATION RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Attempted: {total}
• Successful: {success}
• Failed: {total - success}
• Success Rate: {success/total*100:.1f}%

DATABASE STATUS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Orders in DWH: {total_orders:,}
• Total Revenue: ${total_revenue:,.2f}

 Data generation complete!
"""
        send_telegram_message(report)
        
    except Exception as e:
        print(f"Error getting database stats: {e}")

if __name__ == "__main__":
    print("Starting data generation...")
    generate_orders(1000)
