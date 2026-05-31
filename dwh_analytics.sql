-- Аналитика по заказам в DWH

-- 1. Количество заказов по дням
SELECT 
    DATE(processed_at) as order_date,
    COUNT(*) as total_orders,
    SUM(amount) as total_amount,
    COUNT(DISTINCT user_id) as unique_users
FROM dwh.fact_orders
GROUP BY DATE(processed_at)
ORDER BY order_date DESC
LIMIT 10;

-- 2. Топ продуктов по объему продаж
SELECT 
    product_id,
    COUNT(*) as orders_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_order_value
FROM dwh.fact_orders
GROUP BY product_id
ORDER BY total_revenue DESC
LIMIT 10;

-- 3. Статусная аналитика
SELECT 
    status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (processed_at - created_at))) as avg_processing_seconds
FROM dwh.fact_orders
GROUP BY status;

-- 4. Почасовая активность
SELECT 
    EXTRACT(HOUR FROM processed_at) as hour,
    COUNT(*) as orders_processed,
    SUM(amount) as revenue
FROM dwh.fact_orders
WHERE processed_at IS NOT NULL
GROUP BY EXTRACT(HOUR FROM processed_at)
ORDER BY hour;
