package com.queuepulse.producer.dto;

import lombok.Data;
import java.math.BigDecimal;

@Data
public class OrderDto {
    private String userId;
    private BigDecimal amount;
    private String productId;
}