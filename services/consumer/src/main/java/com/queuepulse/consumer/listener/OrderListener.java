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
            // Извлекаем данные из сообщения
            String orderId = (String) message.get("orderId");
            String userId = (String) message.get("userId");
            BigDecimal amount = new BigDecimal(message.get("amount").toString());
            String productId = (String) message.get("productId");
            
            System.out.println("Received order: " + orderId + " for user: " + userId);
            
            // Создаем Entity
            OrderEntity order = new OrderEntity();
            order.setId(UUID.fromString(orderId));
            order.setUserId(userId);
            order.setAmount(amount);
            order.setProductId(productId);
            order.setStatus("PENDING");
            order.setProcessedAt(LocalDateTime.now());
            
            // Сохраняем в БД
            dwhService.saveOrder(order);
            
            System.out.println("Order processed successfully: " + orderId);
            
        } catch (Exception e) {
            System.err.println("Error processing order: " + e.getMessage());
            e.printStackTrace();
        }
    }
}