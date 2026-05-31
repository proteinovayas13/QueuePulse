import matplotlib.pyplot as plt
import matplotlib.animation as animation
import subprocess
import json
import time
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

# Настройка графиков с правильными интервалами
plt.style.use('dark_background')
fig = plt.figure(figsize=(14, 10))
fig.suptitle('QueuePulse Load Test - Real Time Metrics', fontsize=16, color='cyan', fontweight='bold')

# Создаем 3 графика с правильными интервалами
ax1 = plt.subplot(3, 1, 1)  # CPU
ax2 = plt.subplot(3, 1, 2)  # RPS
ax3 = plt.subplot(3, 1, 3)  # Status

# Данные для графиков
timestamps = []
cpu_data = {'consumer': [], 'producer': [], 'rabbitmq': []}
rps_data = []
queue_data = []

def get_docker_stats():
    """Получение метрик из Docker"""
    try:
        result = subprocess.run(['docker', 'stats', '--no-stream', '--format', 
                                '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}'], 
                               capture_output=True, text=True, timeout=5)
        
        stats = {}
        for line in result.stdout.strip().split('\n'):
            if 'queuepulse' in line and '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    cpu = parts[1].replace('%', '').strip()
                    try:
                        stats[name] = float(cpu)
                    except:
                        stats[name] = 0
        return stats
    except Exception as e:
        print(f"Docker stats error: {e}")
        return {}

def get_rabbitmq_stats():
    """Получение метрик RabbitMQ"""
    try:
        response = requests.get('http://localhost:15672/api/queues', 
                               auth=HTTPBasicAuth('admin', 'admin123'),
                               timeout=3)
        if response.status_code == 200:
            queues = response.json()
            for queue in queues:
                if queue.get('name') == 'order.queue':
                    msg_stats = queue.get('message_stats', {})
                    publish_details = msg_stats.get('publish_details', {})
                    return {
                        'messages': queue.get('messages_ready', 0),
                        'rate': publish_details.get('rate', 0),
                        'consumers': queue.get('consumers', 0)
                    }
    except Exception as e:
        print(f"RabbitMQ error: {e}")
    return {'messages': 0, 'rate': 0, 'consumers': 0}

def update_plot(frame):
    """Обновление графика"""
    global timestamps, cpu_data, rps_data, queue_data
    
    # Получаем данные
    docker_stats = get_docker_stats()
    rabbit_stats = get_rabbitmq_stats()
    
    # Добавляем timestamp
    now = datetime.now()
    timestamps.append(now)
    
    # CPU данные
    cpu_data['consumer'].append(docker_stats.get('queuepulse-consumer', 0))
    cpu_data['producer'].append(docker_stats.get('queuepulse-producer', 0))
    cpu_data['rabbitmq'].append(docker_stats.get('queuepulse-rabbitmq', 0))
    
    # RPS и Queue данные
    rps_data.append(rabbit_stats['rate'])
    queue_data.append(rabbit_stats['messages'])
    
    # Ограничиваем длину (последние 60 секунд)
    max_points = 60
    if len(timestamps) > max_points:
        timestamps.pop(0)
        cpu_data['consumer'].pop(0)
        cpu_data['producer'].pop(0)
        cpu_data['rabbitmq'].pop(0)
        rps_data.pop(0)
        queue_data.pop(0)
    
    # График 1: CPU Usage
    ax1.clear()
    if len(timestamps) > 0:
        ax1.plot(timestamps, cpu_data['consumer'], 'r-', label='Consumer', linewidth=2, marker='o', markersize=3)
        ax1.plot(timestamps, cpu_data['producer'], 'b-', label='Producer', linewidth=2, marker='s', markersize=3)
        ax1.plot(timestamps, cpu_data['rabbitmq'], 'y-', label='RabbitMQ', linewidth=2, marker='^', markersize=3)
    ax1.set_ylabel('CPU %', color='white', fontsize=10)
    ax1.set_title('CPU Usage', color='cyan', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right', facecolor='black', edgecolor='cyan')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.tick_params(colors='white', labelsize=8)
    ax1.set_ylim(0, max(300, max(cpu_data['consumer'] + [100]) + 50))
    
    # График 2: Message Rate
    ax2.clear()
    if len(timestamps) > 0:
        ax2.plot(timestamps, rps_data, 'g-', label='Messages/sec', linewidth=2, marker='d', markersize=3)
        ax2.fill_between(timestamps, rps_data, alpha=0.3, color='green')
    ax2.set_ylabel('RPS', color='white', fontsize=10)
    ax2.set_title('Message Rate (RabbitMQ)', color='cyan', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right', facecolor='black', edgecolor='cyan')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.tick_params(colors='white', labelsize=8)
    if rps_data:
        ax2.set_ylim(0, max(100, max(rps_data) + 20))
    
    # График 3: Queue Status
    ax3.clear()
    ax3.axis('off')
    
    # Текстовый статус с рамкой
    current_cpu_consumer = cpu_data['consumer'][-1] if cpu_data['consumer'] else 0
    current_cpu_producer = cpu_data['producer'][-1] if cpu_data['producer'] else 0
    current_rps = rps_data[-1] if rps_data else 0
    current_queue = queue_data[-1] if queue_data else 0
    
    # Цветовая индикация
    cpu_color = 'red' if current_cpu_consumer > 200 else 'yellow' if current_cpu_consumer > 100 else 'lime'
    rps_color = 'red' if current_rps > 80 else 'yellow' if current_rps > 40 else 'lime'
    queue_color = 'red' if current_queue > 100 else 'yellow' if current_queue > 50 else 'lime'
    
    status_text = f"""
*************************************************************
                    CURRENT STATUS                          
*************************************************************
                                                           
 Consumer CPU:  {current_cpu_consumer:>6.1f}%                                      
 Producer CPU:  {current_cpu_producer:>6.1f}%                                      
                                                           
  Messages/sec:  {current_rps:>6.1f}                                       
  Queue size:    {current_queue:>6}                                         
  Consumers:     {rabbit_stats['consumers']:>6}                                         
                                                            
*************************************************************
    """
    
    ax3.text(0.5, 0.5, status_text, transform=ax3.transAxes, 
             fontsize=10, verticalalignment='center', horizontalalignment='center',
             bbox=dict(boxstyle='round', facecolor='black', alpha=0.8, edgecolor='cyan'),
             color='white', family='monospace')
    
    # Автоматическая настройка отступов
    plt.tight_layout()
    fig.subplots_adjust(top=0.92, hspace=0.4)

# Запускаем анимацию
print("Starting live monitoring...")
print("Press Ctrl+C to stop\n")

ani = animation.FuncAnimation(fig, update_plot, interval=2000, cache_frame_data=False)
plt.show()
