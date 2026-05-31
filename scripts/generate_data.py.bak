import requests
import time
import random
import sys

def generate_1000_orders(url='http://localhost:8080'):
    print("Generating 1000 orders...")
    
    users = [f'user_{i:04d}' for i in range(1, 101)]
    products = [f'prod_{i:04d}' for i in range(1, 51)]
    
    success = 0
    for i in range(1000):
        order = {
            'userId': random.choice(users),
            'amount': round(random.uniform(10, 1000), 2),
            'productId': random.choice(products)
        }
        
        try:
            resp = requests.post(f'{url}/api/orders', json=order, timeout=1)
            if resp.status_code == 202:
                success += 1
        except:
            pass
        
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i+1}/1000")
    
    print(f"\nCompleted: {success}/1000 successful")

if __name__ == '__main__':
    generate_1000_orders()