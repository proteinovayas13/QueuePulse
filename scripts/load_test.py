import requests
import time
import threading
import statistics
from datetime import datetime
import json

class LoadTest:
    def __init__(self, url='http://localhost:8080'):
        self.url = url
        self.results = []
    
    def smoke_test(self):
        print("[1/5] Smoke test")
        try:
            resp = requests.get(f'{self.url}/api/orders/health', timeout=5)
            assert resp.status_code == 200
            print("  OK")
            return True
        except:
            print("  FAILED")
            return False
    
    def load_test(self, total=1000, concurrency=10):
        print(f"[2/5] Load test: {total} requests, {concurrency} concurrent")
        
        def worker(n):
            for _ in range(n):
                start = time.time()
                resp = requests.post(f'{self.url}/api/orders', json={
                    'userId': 'load_user',
                    'amount': 100,
                    'productId': 'test'
                })
                self.results.append((time.time() - start) * 1000)
        
        threads = []
        per_thread = total // concurrency
        for _ in range(concurrency):
            t = threading.Thread(target=worker, args=(per_thread,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        latencies = self.results
        print(f"  Success: {len(latencies)}/{total}")
        print(f"  Avg: {statistics.mean(latencies):.1f}ms")
        if len(latencies) >= 100:
            print(f"  P95: {statistics.quantiles(latencies, n=100)[94]:.1f}ms")
    
    def spike_test(self, duration=30, rate=100):
        print(f"[3/5] Spike test: {duration}s at {rate} RPS")
        end = time.time() + duration
        count = 0
        errors = 0
        
        while time.time() < end:
            for _ in range(rate // 10):
                try:
                    requests.post(f'{self.url}/api/orders', json={'userId': 'spike', 'amount': 100})
                    count += 1
                except:
                    errors += 1
            time.sleep(0.1)
        
        print(f"  Requests: {count}, Errors: {errors}")
    
    def stress_test(self, start=10, end=200, step=20):
        print(f"[4/5] Stress test: {start} to {end} RPS")
        
        for rps in range(start, end + 1, step):
            count = 0
            end_time = time.time() + 10
            interval = 1.0 / rps
            
            while time.time() < end_time:
                start_t = time.time()
                try:
                    requests.post(f'{self.url}/api/orders', json={'userId': 'stress', 'amount': 100})
                    count += 1
                except:
                    pass
                elapsed = time.time() - start_t
                if elapsed < interval:
                    time.sleep(interval - elapsed)
            
            print(f"  {rps} RPS target -> {count} requests/10s")
    
    def analyze(self):
        print("[5/5] Analysis")
        
        stats_resp = requests.get(f'{self.url}/api/orders/stats').json()
        
        print(f"\n=== RESULTS ===")
        print(f"Total requests: {stats_resp['total']}")
        print(f"Success rate: {stats_resp['successRate']:.1f}%")
        
        if self.results:
            latencies = self.results
            print(f"Avg latency: {statistics.mean(latencies):.1f}ms")
            print(f"Min latency: {min(latencies):.1f}ms")
            print(f"Max latency: {max(latencies):.1f}ms")
    
    def run(self):
        if not self.smoke_test():
            return
        self.load_test(1000, 20)
        self.spike_test(30, 100)
        self.stress_test(10, 200, 30)
        self.analyze()

if __name__ == '__main__':
    test = LoadTest()
    test.run()