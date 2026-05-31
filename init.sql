CREATE SCHEMA IF NOT EXISTS dwh;

CREATE TABLE IF NOT EXISTS dwh.fact_orders (
    id UUID PRIMARY KEY,
    user_id VARCHAR(100),
    amount DECIMAL(12,2),
    product_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE INDEX idx_fact_created ON dwh.fact_orders(created_at);
CREATE INDEX idx_fact_user ON dwh.fact_orders(user_id);

CREATE TABLE IF NOT EXISTS dwh.load_test_results (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(50),
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_requests INTEGER,
    success_count INTEGER,
    error_count INTEGER,
    avg_latency_ms DECIMAL(10,2),
    p95_latency_ms DECIMAL(10,2),
    p99_latency_ms DECIMAL(10,2),
    rps DECIMAL(10,2)
);