package com.threatshield.backend.test;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
public class AdminTestController {

    @GetMapping("/dashboard")
    public String adminDashboard() {
        return "Welcome Admin! You have ADMIN access.";
    }
}