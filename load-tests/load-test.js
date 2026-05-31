import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 50 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],
        http_req_failed: ['rate<0.05'],
    },
};

export default function () {
    const payload = JSON.stringify({
        userId: `user_${__VU}`,
        amount: Math.random() * 1000,
        productId: `prod_${Math.floor(Math.random() * 50)}`,
    });
    
    const res = http.post('http://producer:8080/api/orders', payload, {
        headers: { 'Content-Type': 'application/json' },
    });
    
    check(res, { 'status is 202': (r) => r.status === 202 });
    sleep(0.1);
}