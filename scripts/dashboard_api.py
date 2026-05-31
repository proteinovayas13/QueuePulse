# scripts/dashboard_api.py
from flask import Flask, jsonify
import psycopg2
import subprocess
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="queuepulse",
        user="queuepulse",
        password="queuepulse123"
    )

def get_docker_stats():
    try:
        result = subprocess.run(
            ['docker', 'stats', '--no-stream', '--format', '{{.Name}}|{{.CPUPerc}}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        stats = {'consumer': 0, 'producer': 0}
        for line in result.stdout.strip().split('\n'):
            if 'queuepulse-consumer' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    stats['consumer'] = float(parts[1].replace('%', '').strip())
            elif 'queuepulse-producer' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    stats['producer'] = float(parts[1].replace('%', '').strip())
        return stats
    except Exception as e:
        print(f"Docker error: {e}")
        return {'consumer': 0, 'producer': 0}

def get_rabbitmq_stats():
    try:
        response = requests.get(
            'http://localhost:15672/api/queues',
            auth=HTTPBasicAuth('admin', 'admin123'),
            timeout=3
        )
        if response.status_code == 200:
            queues = response.json()
            for queue in queues:
                if queue.get('name') == 'order.queue':
                    msg_stats = queue.get('message_stats', {})
                    publish_details = msg_stats.get('publish_details', {})
                    return {
                        'messages_ready': queue.get('messages_ready', 0),
                        'messages_unack': queue.get('messages_unacknowledged', 0),
                        'consumers': queue.get('consumers', 0),
                        'publish_rate': publish_details.get('rate', 0)
                    }
    except Exception as e:
        print(f"RabbitMQ error: {e}")
    return {'messages_ready': 0, 'messages_unack': 0, 'consumers': 0, 'publish_rate': 0}

def get_dwh_metrics():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM dwh.fact_orders")
        total_orders = cur.fetchone()[0] or 0
        
        cur.execute("SELECT ROUND(SUM(amount)::numeric, 2) FROM dwh.fact_orders")
        total_revenue = cur.fetchone()[0] or 0
        
        cur.execute("SELECT ROUND(AVG(amount)::numeric, 2) FROM dwh.fact_orders")
        avg_order = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM dwh.fact_orders")
        unique_customers = cur.fetchone()[0] or 0
        
        cur.execute("""
            SELECT product_id, COUNT(*) as orders, ROUND(SUM(amount)::numeric, 2) as revenue
            FROM dwh.fact_orders
            GROUP BY product_id
            ORDER BY revenue DESC
            LIMIT 5
        """)
        top_products = [{'product_id': row[0], 'orders': row[1], 'revenue': float(row[2])} 
                        for row in cur.fetchall()]
        
        conn.close()
        
        return {
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'avg_order': float(avg_order),
            'unique_customers': unique_customers,
            'top_products': top_products
        }
    except Exception as e:
        print(f"DWH error: {e}")
        return {
            'total_orders': 0,
            'total_revenue': 0,
            'avg_order': 0,
            'unique_customers': 0,
            'top_products': []
        }

def check_service_health():
    services = {
        'producer': False,
        'consumer': False,
        'rabbitmq': False,
        'postgres': False
    }
    
    try:
        response = requests.get('http://localhost:8080/api/orders/health', timeout=2)
        services['producer'] = response.status_code == 200
    except:
        pass
    
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=queuepulse-consumer', '--format', '{{.Status}}'],
                               capture_output=True, text=True)
        services['consumer'] = 'Up' in result.stdout
    except:
        pass
    
    try:
        response = requests.get('http://localhost:15672/api/health/checks/alarms',
                               auth=HTTPBasicAuth('admin', 'admin123'), timeout=2)
        services['rabbitmq'] = response.status_code == 200
    except:
        pass
    
    try:
        result = subprocess.run(['docker', 'exec', 'queuepulse-postgres', 'pg_isready', '-U', 'queuepulse'],
                               capture_output=True, text=True)
        services['postgres'] = 'accepting connections' in result.stdout
    except:
        pass
    
    return services

@app.route('/api/metrics')
def get_metrics():
    docker_stats = get_docker_stats()
    rabbitmq_stats = get_rabbitmq_stats()
    dwh_metrics = get_dwh_metrics()
    health = check_service_health()
    
    return jsonify({
        'total_orders': dwh_metrics['total_orders'],
        'total_revenue': dwh_metrics['total_revenue'],
        'avg_order': dwh_metrics['avg_order'],
        'unique_customers': dwh_metrics['unique_customers'],
        'top_products': dwh_metrics['top_products'],
        'cpu_consumer': docker_stats['consumer'],
        'cpu_producer': docker_stats['producer'],
        'messages_ready': rabbitmq_stats['messages_ready'],
        'messages_unack': rabbitmq_stats['messages_unack'],
        'consumers': rabbitmq_stats['consumers'],
        'publish_rate': rabbitmq_stats['publish_rate'],
        'producer_status': health['producer'],
        'consumer_status': health['consumer'],
        'rabbitmq_status': health['rabbitmq'],
        'postgres_status': health['postgres'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/')
def serve_dashboard():
    from flask import send_file
    return send_file('../docs/index.html')

if __name__ == '__main__':
    print("Dashboard API running at http://localhost:5000")
    print("Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=False)