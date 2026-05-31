package com.queuepulse.consumer.listener;

import com.queuepulse.consumer.entity.OrderEntity;
import com.queuepulse.consumer.service.DwhService;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Component
public class OrderListener {
    
    @Autowired
    private DwhService dwhService;
    
    @RabbitListener(queues = "order.queue")
    public void receiveOrder(Map<String, Object> message) {
        try {
            System.out.println("Received message: " + message);
            
            // Extract data with null checks
            String orderId = (String) message.get("orderId");
            if (orderId == null) {
                System.err.println("orderId is null");
                return;
            }
            
            String userId = (String) message.get("userId");
            if (userId == null) {
                userId = "unknown_user";
            }
            
            String productId = (String) message.get("productId");
            if (productId == null) {
                productId = "unknown_product";
            }
            
            BigDecimal amount = null;
            Object amountObj = message.get("amount");
            if (amountObj instanceof BigDecimal) {
                amount = (BigDecimal) amountObj;
            } else if (amountObj instanceof Number) {
                amount = BigDecimal.valueOf(((Number) amountObj).doubleValue());
            } else if (amountObj instanceof String) {
                amount = new BigDecimal((String) amountObj);
            } else {
                amount = BigDecimal.ZERO;
            }
            
            System.out.println("Processing order: " + orderId + " for user: " + userId + " amount: " + amount);
            
            // Create entity
            OrderEntity order = new OrderEntity();
            order.setId(UUID.fromString(orderId));
            order.setUserId(userId);
            order.setAmount(amount);
            order.setProductId(productId);
            order.setStatus("PROCESSED");
            order.setProcessedAt(LocalDateTime.now());
            
            // Save to DWH
            dwhService.saveOrder(order);
            System.out.println("Order saved successfully: " + orderId);
            
        } catch (Exception e) {
            System.err.println("Error processing order: " + e.getMessage());
            e.printStackTrace();
        }
    }
}