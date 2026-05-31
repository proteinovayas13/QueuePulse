import requests
import json
from datetime import datetime

def analyze():
    stats = requests.get('http://localhost:8080/api/orders/stats').json()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_requests': stats['total'],
        'success_rate': stats['successRate'],
        'system_health': 'ok'
    }
    
    print(json.dumps(report, indent=2))
    
    with open('results/test_report.json', 'w') as f:
        json.dump(report, f, indent=2)

if __name__ == '__main__':
    analyze()