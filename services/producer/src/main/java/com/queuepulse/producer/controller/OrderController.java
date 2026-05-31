package com.queuepulse.producer.controller;

import com.queuepulse.producer.dto.OrderDto;
import com.queuepulse.producer.service.RabbitMqService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @Autowired
    private RabbitMqService rabbitMqService;
    
    private AtomicLong totalRequests = new AtomicLong(0);
    private AtomicLong successRequests = new AtomicLong(0);
    
    @PostMapping
    public ResponseEntity<Map<String, String>> createOrder(@RequestBody OrderDto order) {
        totalRequests.incrementAndGet();
        
        String orderId = rabbitMqService.sendOrder(
            order.getUserId(), 
            order.getAmount(), 
            order.getProductId()
        );
        
        successRequests.incrementAndGet();
        
        Map<String, String> response = new HashMap<>();
        response.put("orderId", orderId);
        response.put("status", "accepted");
        return ResponseEntity.accepted().body(response);
    }
    
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("total", totalRequests.get());
        stats.put("success", successRequests.get());
        stats.put("successRate", successRequests.get() * 100.0 / Math.max(totalRequests.get(), 1));
        return ResponseEntity.ok(stats);
    }
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "up");
        return ResponseEntity.ok(response);
    }
}