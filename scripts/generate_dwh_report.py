# scripts/generate_dwh_report.py
import psycopg2
import json
from datetime import datetime
import os

def get_metrics():
    """Get DWH metrics"""
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
        
        cur.execute("SELECT ROUND(SUM(amount)::numeric, 2) FROM dwh.fact_orders")
        total_revenue = cur.fetchone()[0] or 0
        
        cur.execute("SELECT ROUND(AVG(amount)::numeric, 2) FROM dwh.fact_orders")
        avg_order = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM dwh.fact_orders")
        unique_customers = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*), ROUND(SUM(amount)::numeric, 2)
            FROM dwh.fact_orders
            WHERE processed_at >= NOW() - INTERVAL '24 hours'
        """)
        last_24h_orders, last_24h_revenue = cur.fetchone()
        last_24h_orders = last_24h_orders or 0
        last_24h_revenue = last_24h_revenue or 0
        
        conn.close()
        
        metrics = f"""

TOTAL STATISTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
* Total Orders: {total_orders:,}
* Total Revenue: ${total_revenue:,.2f}
* Average Order: ${avg_order:.2f}
* Unique Customers: {unique_customers:,}

LAST 24 HOURS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
* Orders: {last_24h_orders:,}
* Revenue: ${last_24h_revenue:,.2f}

System Status: HEALTHY
DWH: OPERATIONAL
        """
        
        # Save to file
        with open('dwh_report.txt', 'w') as f:
            f.write(metrics)
        
        # Set output for GitHub Actions
        with open(os.environ.get('GITHUB_OUTPUT', 'output.txt'), 'a') as f:
            f.write(f"message={metrics.replace(chr(10), ' ')}")
        
        print(metrics)
        
    except Exception as e:
        error_msg = f"Database error: {e}"
        print(error_msg)
        with open('dwh_report.txt', 'w') as f:
            f.write(error_msg)

if __name__ == "__main__":
    get_metrics()
