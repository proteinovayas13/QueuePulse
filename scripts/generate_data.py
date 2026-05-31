import requests
import time
import random
import json

def generate_orders(count=100):
    print(f"Generating {count} orders...")
    
    success = 0
    for i in range(count):
        try:
            order = {
                "userId": f"user_{random.randint(1, 100)}",
                "amount": round(random.uniform(10, 1000), 2),
                "productId": f"prod_{random.randint(1, 50):04d}"
            }
            
            response = requests.post(
                "http://localhost:8080/api/orders",
                json=order,
                headers={"Content-Type": "application/json"},
                timeout=2
            )
            
            if response.status_code in [200, 201, 202]:
                success += 1
            
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i + 1}/{count}")
                
        except Exception as e:
            print(f"  Error: {e}")
        
        time.sleep(0.01)
    
    print(f"\nResult: {success}/{count} successful")

if __name__ == "__main__":
    generate_orders(100)
