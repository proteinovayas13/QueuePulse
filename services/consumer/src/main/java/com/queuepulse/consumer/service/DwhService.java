package com.queuepulse.consumer.service;

import com.queuepulse.consumer.entity.OrderEntity;
import org.springframework.stereotype.Service;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.transaction.Transactional;
import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class DwhService {
    
    @PersistenceContext
    private EntityManager entityManager;
    
    @Transactional
    public void saveOrder(OrderEntity order) {
        if (order == null) {
            return;
        }
        order.setProcessedAt(LocalDateTime.now());
        order.setStatus("PROCESSED");
        entityManager.persist(order);
        System.out.println("Order saved: " + order.getId());
    }
}