package com.queuepulse.producer.service;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.UUID;
import java.util.HashMap;
import java.util.Map;
import java.math.BigDecimal;  

@Service
public class RabbitMqService {
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    public String sendOrder(String userId, BigDecimal amount, String productId) {
        String orderId = UUID.randomUUID().toString();
        
        Map<String, Object> message = new HashMap<>();
        message.put("orderId", orderId);
        message.put("userId", userId);
        message.put("amount", amount);
        message.put("productId", productId);
        
        rabbitTemplate.convertAndSend("order.queue", message);
        return orderId;
    }
}