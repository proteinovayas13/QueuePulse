import psycopg2
import pandas as pd
from datetime import datetime

def run_dwh_analytics():
    """Run DWH analytics"""
    
    # Connection to DB
    conn = psycopg2.connect(
        host="localhost",
        database="queuepulse",
        user="queuepulse",
        password="queuepulse123"
    )
    

    print("QUEUEPULSE DWH ANALYTICS REPORT")

    print(f"Report generated: {datetime.now()}\n")
    
    # 1. Daily statistics
    print("DAILY ORDER STATISTICS:")

    df_daily = pd.read_sql("""
        SELECT 
            DATE(processed_at) as order_date,
            COUNT(*) as orders,
            SUM(amount) as revenue,
            COUNT(DISTINCT user_id) as unique_users
        FROM dwh.fact_orders
        WHERE processed_at IS NOT NULL
        GROUP BY DATE(processed_at)
        ORDER BY order_date DESC
        LIMIT 7
    """, conn)
    
    if len(df_daily) > 0:
        for _, row in df_daily.iterrows():
            print(f"  {row['order_date']}: {row['orders']} orders | ${row['revenue']:.2f} | {row['unique_users']} users")
    else:
        print("No data available")
    
    # 2. Top products
    print("\nTOP 10 PRODUCTS BY REVENUE:")

    df_products = pd.read_sql("""
        SELECT 
            product_id,
            COUNT(*) as orders,
            SUM(amount) as revenue,
            AVG(amount) as avg_price
        FROM dwh.fact_orders
        GROUP BY product_id
        ORDER BY revenue DESC
        LIMIT 10
    """, conn)
    
    if len(df_products) > 0:
        for idx, row in df_products.iterrows():
            print(f"  {idx+1}. Product {row['product_id'][:15]}: {row['orders']} orders | ${row['revenue']:.2f}")
    else:
        print("  No data available")
    
    # 3. Status analytics
    print("\nORDER STATUS BREAKDOWN:")
    df_status = pd.read_sql("""
        SELECT 
            status,
            COUNT(*) as count,
            ROUND(AVG(EXTRACT(EPOCH FROM (processed_at - created_at)))) as avg_processing_sec
        FROM dwh.fact_orders
        GROUP BY status
    """, conn)
    
    if len(df_status) > 0:
        for _, row in df_status.iterrows():
            print(f"{row['status']}: {row['count']} orders (avg processing: {row['avg_processing_sec']:.0f} sec)")
    else:
        print("No data available")
    
    # 4. Hourly activity
    print("\nHOURLY ACTIVITY PATTERN:")
    df_hourly = pd.read_sql("""
        SELECT 
            EXTRACT(HOUR FROM processed_at) as hour,
            COUNT(*) as orders,
            SUM(amount) as revenue
        FROM dwh.fact_orders
        WHERE processed_at IS NOT NULL
        GROUP BY EXTRACT(HOUR FROM processed_at)
        ORDER BY hour
    """, conn)
    
    if len(df_hourly) > 0 and df_hourly['orders'].max() > 0:
        for _, row in df_hourly.iterrows():
            bar_length = int(row['orders'] / df_hourly['orders'].max() * 30)
            bar = "#" * bar_length if bar_length > 0 else ""
            print(f"{int(row['hour']):02d}:00 | {bar} {row['orders']} orders")
    else:
        print("No data available")
    
    # 5. Total statistics
    print("\nTOTAL STATISTICS:")
    df_total = pd.read_sql("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(amount) as total_revenue,
            AVG(amount) as avg_order_value,
            COUNT(DISTINCT user_id) as total_customers
        FROM dwh.fact_orders
    """, conn)
    
    total_orders = df_total['total_orders'].iloc[0] if len(df_total) > 0 else 0
    total_revenue = df_total['total_revenue'].iloc[0] if len(df_total) > 0 else 0
    avg_order = df_total['avg_order_value'].iloc[0] if len(df_total) > 0 else 0
    total_customers = df_total['total_customers'].iloc[0] if len(df_total) > 0 else 0
    
    print(f"Total Orders: {total_orders:,}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Average Order Value: ${avg_order:.2f}")
    print(f"Unique Customers: {total_customers:,}")
    
    conn.close()
    print("DWH Analytics Complete")

if __name__ == "__main__":
    run_dwh_analytics()
