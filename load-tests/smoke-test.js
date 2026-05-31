import http from 'k6/http';
import { check } from 'k6';

export const options = {
    vus: 1,
    duration: '10s',
};

export default function () {
    const res = http.get('http://producer:8080/api/orders/health');
    check(res, {
        'status is 200': (r) => r.status === 200,
    });
}