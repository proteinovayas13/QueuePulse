package com.queuepulse.consumer.entity;

import lombok.Data;
import javax.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "fact_orders", schema = "dwh")
@Data
public class OrderEntity {
    @Id
    private UUID id;
    
    @Column(name = "user_id")
    private String userId;
    
    @Column(name = "amount")
    private BigDecimal amount;
    
    @Column(name = "product_id")
    private String productId;
    
    @Column(name = "status")
    private String status;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "processed_at")
    private LocalDateTime processedAt;
}