package com.queuepulse.mock;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.util.Map;
import java.util.HashMap;

@RestController
public class PaymentMockController {
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "UP");
        return ResponseEntity.ok(response);
    }
    
    @PostMapping("/api/payments")
    public ResponseEntity<Map<String, String>> processPayment(@RequestBody Map<String, Object> payment) {
        Map<String, String> response = new HashMap<>();
        response.put("status", "SUCCESS");
        response.put("paymentId", java.util.UUID.randomUUID().toString());
        return ResponseEntity.ok(response);
    }
}
