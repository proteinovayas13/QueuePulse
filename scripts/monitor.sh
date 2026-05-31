#!/bin/bash

while true; do
    clear
    echo "=== QueuePulse Monitor ==="
    echo "Time: $(date)"
    echo ""
    
    echo "Producer Stats:"
    curl -s http://localhost:8080/api/orders/stats | python -m json.tool 2>/dev/null
    
    echo ""
    echo "Database Count:"
    docker exec queuepulse-postgres psql -U queuepulse -d queuepulse -t -c "SELECT COUNT(*) FROM dwh.fact_orders;" 2>/dev/null
    
    echo ""
    echo "RabbitMQ Queues:"
    docker exec queuepulse-rabbitmq rabbitmqctl list_queues 2>/dev/null | grep order
    
    sleep 5
done